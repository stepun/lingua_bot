"""Export service for PDF and TXT generation"""

import os
import io
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import aiofiles
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import logging

from bot.database import db
from config import config

logger = logging.getLogger(__name__)

class ExportService:
    def __init__(self):
        self.setup_fonts()

    def setup_fonts(self):
        """Setup fonts for PDF generation"""
        try:
            # Try to register system fonts for better Unicode support
            font_paths = [
                '/System/Library/Fonts/Arial.ttf',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:/Windows/Fonts/arial.ttf',  # Windows
                'C:/Windows/Fonts/calibri.ttf'  # Windows
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                        self.custom_font = 'CustomFont'
                        break
                    except:
                        continue
            else:
                self.custom_font = 'Helvetica'

        except Exception as e:
            logger.warning(f"Font setup failed: {e}")
            self.custom_font = 'Helvetica'

    async def export_history_to_pdf(self, user_id: int, history: List[Dict[str, Any]]) -> Optional[bytes]:
        """Export translation history to PDF"""
        try:
            # Create PDF buffer
            buffer = io.BytesIO()

            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )

            # Get user info
            user_info = await db.get_user(user_id)
            user_name = user_info.get('first_name', 'Пользователь')

            # Create styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.custom_font,
                fontSize=20,
                spaceAfter=30,
                alignment=1,  # Center
                textColor=colors.darkblue
            )

            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontName=self.custom_font,
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.darkgreen
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=self.custom_font,
                fontSize=11,
                spaceAfter=6
            )

            # Build story
            story = []

            # Title
            title = Paragraph("📚 Мой Разговорник", title_style)
            story.append(title)

            # User info
            user_info_text = f"Пользователь: {user_name}<br/>Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>Всего переводов: {len(history)}"
            user_para = Paragraph(user_info_text, normal_style)
            story.append(user_para)
            story.append(Spacer(1, 20))

            # Statistics
            if history:
                # Count languages
                source_langs = {}
                target_langs = {}
                for item in history:
                    src_lang = item.get('source_language', 'Unknown')
                    tgt_lang = item.get('target_language', 'Unknown')
                    source_langs[src_lang] = source_langs.get(src_lang, 0) + 1
                    target_langs[tgt_lang] = target_langs.get(tgt_lang, 0) + 1

                # Most used languages
                most_used_source = max(source_langs.items(), key=lambda x: x[1]) if source_langs else ('N/A', 0)
                most_used_target = max(target_langs.items(), key=lambda x: x[1]) if target_langs else ('N/A', 0)

                stats_text = f"""
                <b>📊 Статистика использования:</b><br/>
                • Чаще всего переводил с: {config.SUPPORTED_LANGUAGES.get(most_used_source[0], most_used_source[0])} ({most_used_source[1]} раз)<br/>
                • Чаще всего переводил на: {config.SUPPORTED_LANGUAGES.get(most_used_target[0], most_used_target[0])} ({most_used_target[1]} раз)<br/>
                • Голосовых переводов: {sum(1 for item in history if item.get('is_voice', False))}
                """
                stats_para = Paragraph(stats_text, normal_style)
                story.append(stats_para)
                story.append(Spacer(1, 20))

            # Translations
            story.append(Paragraph("📝 Переводы", subtitle_style))

            if not history:
                no_history_para = Paragraph("История переводов пуста.", normal_style)
                story.append(no_history_para)
            else:
                # Group by date
                translations_by_date = {}
                for item in history:
                    # Handle both datetime objects and strings
                    created_at = item['created_at']
                    if isinstance(created_at, datetime):
                        date_str = created_at.strftime('%Y-%m-%d')
                    else:
                        date_str = created_at[:10]  # Get date part
                    if date_str not in translations_by_date:
                        translations_by_date[date_str] = []
                    translations_by_date[date_str].append(item)

                # Sort dates (newest first)
                sorted_dates = sorted(translations_by_date.keys(), reverse=True)

                for date in sorted_dates:
                    # Date header
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    date_formatted = date_obj.strftime('%d.%m.%Y')
                    date_para = Paragraph(f"📅 {date_formatted}", subtitle_style)
                    story.append(date_para)

                    # Translations for this date
                    for i, item in enumerate(translations_by_date[date]):
                        # Translation item
                        source_text = item['source_text']
                        translated_text = item['translated_text']
                        source_lang = config.SUPPORTED_LANGUAGES.get(item.get('source_language', ''), item.get('source_language', ''))
                        target_lang = config.SUPPORTED_LANGUAGES.get(item.get('target_language', ''), item.get('target_language', ''))
                        # Handle both datetime objects and strings
                        created_at = item['created_at']
                        if isinstance(created_at, datetime):
                            time_str = created_at.strftime('%H:%M')
                        else:
                            time_str = created_at[11:16]  # Get time part
                        voice_icon = "🎤 " if item.get('is_voice', False) else ""

                        translation_text = f"""
                        <b>{voice_icon}🔸 {source_lang} → {target_lang}</b> ({time_str})<br/>
                        <i>Оригинал:</i> {source_text}<br/>
                        <i>Перевод:</i> {translated_text}
                        """

                        translation_para = Paragraph(translation_text, normal_style)
                        story.append(translation_para)
                        story.append(Spacer(1, 10))

            # Footer
            story.append(Spacer(1, 30))
            footer_text = f"Создано с помощью PolyglotAI44 🤖<br/>Telegram: @PolyglotAI44_bot<br/>{datetime.now().strftime('%d.%m.%Y %H:%M')}"
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontName=self.custom_font,
                fontSize=9,
                alignment=1,
                textColor=colors.grey
            )
            footer_para = Paragraph(footer_text, footer_style)
            story.append(footer_para)

            # Build PDF
            doc.build(story)

            # Get PDF data
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()

            return pdf_data

        except Exception as e:
            logger.error(f"PDF export error: {e}")
            return None

    async def export_history_to_txt(self, user_id: int, history: List[Dict[str, Any]]) -> Optional[bytes]:
        """Export translation history to TXT"""
        try:
            # Get user info
            user_info = await db.get_user(user_id)
            user_name = user_info.get('first_name', 'Пользователь')

            # Create text content
            content = []
            content.append("📚 МОЙ РАЗГОВОРНИК")
            content.append("=" * 50)
            content.append(f"Пользователь: {user_name}")
            content.append(f"Создано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            content.append(f"Всего переводов: {len(history)}")
            content.append("")

            if not history:
                content.append("История переводов пуста.")
            else:
                # Statistics
                source_langs = {}
                target_langs = {}
                voice_count = 0

                for item in history:
                    src_lang = item.get('source_language', 'Unknown')
                    tgt_lang = item.get('target_language', 'Unknown')
                    source_langs[src_lang] = source_langs.get(src_lang, 0) + 1
                    target_langs[tgt_lang] = target_langs.get(tgt_lang, 0) + 1
                    if item.get('is_voice', False):
                        voice_count += 1

                if source_langs:
                    most_used_source = max(source_langs.items(), key=lambda x: x[1])
                    most_used_target = max(target_langs.items(), key=lambda x: x[1])

                    content.append("📊 СТАТИСТИКА ИСПОЛЬЗОВАНИЯ:")
                    content.append(f"• Чаще всего переводил с: {config.SUPPORTED_LANGUAGES.get(most_used_source[0], most_used_source[0])} ({most_used_source[1]} раз)")
                    content.append(f"• Чаще всего переводил на: {config.SUPPORTED_LANGUAGES.get(most_used_target[0], most_used_target[0])} ({most_used_target[1]} раз)")
                    content.append(f"• Голосовых переводов: {voice_count}")
                    content.append("")

                # Group by date
                translations_by_date = {}
                for item in history:
                    # Handle both datetime objects and strings
                    created_at = item['created_at']
                    if isinstance(created_at, datetime):
                        date_str = created_at.strftime('%Y-%m-%d')
                    else:
                        date_str = created_at[:10]
                    if date_str not in translations_by_date:
                        translations_by_date[date_str] = []
                    translations_by_date[date_str].append(item)

                # Sort dates (newest first)
                sorted_dates = sorted(translations_by_date.keys(), reverse=True)

                content.append("📝 ПЕРЕВОДЫ:")
                content.append("")

                for date in sorted_dates:
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    date_formatted = date_obj.strftime('%d.%m.%Y')
                    content.append(f"📅 {date_formatted}")
                    content.append("-" * 30)

                    for item in translations_by_date[date]:
                        source_text = item['source_text']
                        translated_text = item['translated_text']
                        source_lang = config.SUPPORTED_LANGUAGES.get(item.get('source_language', ''), item.get('source_language', ''))
                        target_lang = config.SUPPORTED_LANGUAGES.get(item.get('target_language', ''), item.get('target_language', ''))
                        # Handle both datetime objects and strings
                        created_at = item['created_at']
                        if isinstance(created_at, datetime):
                            time_str = created_at.strftime('%H:%M')
                        else:
                            time_str = created_at[11:16]
                        voice_icon = "🎤 " if item.get('is_voice', False) else ""

                        content.append(f"{voice_icon}🔸 {source_lang} → {target_lang} ({time_str})")
                        content.append(f"   Оригинал: {source_text}")
                        content.append(f"   Перевод:  {translated_text}")
                        content.append("")

            # Footer
            content.append("=" * 50)
            content.append("Создано с помощью PolyglotAI44 🤖")
            content.append("Telegram: @PolyglotAI44_bot")
            content.append(f"{datetime.now().strftime('%d.%m.%Y %H:%M')}")

            # Convert to bytes
            text_content = "\n".join(content)
            return text_content.encode('utf-8')

        except Exception as e:
            logger.error(f"TXT export error: {e}")
            return None

    async def save_export_file(self, file_data: bytes, filename: str) -> Optional[str]:
        """Save export file to disk"""
        try:
            file_path = config.EXPORTS_DIR / filename

            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)

            return str(file_path)

        except Exception as e:
            logger.error(f"File save error: {e}")
            return None

    async def generate_export_filename(self, user_id: int, format_type: str) -> str:
        """Generate export filename"""
        user_info = await db.get_user(user_id)
        username = user_info.get('username', f'user_{user_id}')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        return f"lingua_export_{username}_{timestamp}.{format_type}"

    async def cleanup_old_exports(self, max_age_hours: int = 24):
        """Clean up old export files"""
        try:
            import time
            current_time = time.time()
            exports_dir = Path(config.EXPORTS_DIR)

            for file_path in exports_dir.glob("lingua_export_*"):
                file_age = current_time - file_path.stat().st_mtime
                if file_age > (max_age_hours * 3600):
                    file_path.unlink()
                    logger.info(f"Cleaned up old export file: {file_path}")

        except Exception as e:
            logger.error(f"Export cleanup error: {e}")