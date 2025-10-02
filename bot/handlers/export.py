"""Export handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.exceptions import TelegramBadRequest
import logging

from bot.database import db
from bot.services.export import ExportService
from bot.keyboards.inline import get_main_menu_keyboard, get_export_format_keyboard
from bot.utils.messages import get_text

logger = logging.getLogger(__name__)
router = Router()

export_service = ExportService()

@router.callback_query(F.data == "export_pdf")
async def export_pdf_handler(callback: CallbackQuery):
    """Export history to PDF"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.answer("❌ Экспорт доступен только в премиум версии", show_alert=True)
        return

    # Show processing message
    await callback.message.edit_text("📄 Генерирую PDF файл...")

    try:
        # Get user's translation history
        history = await db.get_user_history(callback.from_user.id, limit=100)

        if not history:
            await callback.message.edit_text(
                "📄 История переводов пуста. Сначала сделайте несколько переводов.",
                reply_markup=get_main_menu_keyboard(True)
            )
            return

        # Generate PDF
        pdf_data = await export_service.export_history_to_pdf(callback.from_user.id, history)

        if not pdf_data:
            await callback.message.edit_text(
                "❌ Ошибка при создании PDF файла. Попробуйте позже.",
                reply_markup=get_main_menu_keyboard(True)
            )
            return

        # Generate filename
        filename = await export_service.generate_export_filename(callback.from_user.id, 'pdf')

        # Create file for sending
        pdf_file = BufferedInputFile(pdf_data, filename=filename)

        # Send PDF file
        from datetime import datetime
        first_date = history[0]['created_at']
        last_date = history[-1]['created_at']
        first_date_str = first_date.strftime('%Y-%m-%d') if isinstance(first_date, datetime) else first_date[:10]
        last_date_str = last_date.strftime('%Y-%m-%d') if isinstance(last_date, datetime) else last_date[:10]

        await callback.message.answer_document(
            pdf_file,
            caption=f"📚 Ваш персональный разговорник\n\n"
                   f"📊 Переводов: {len(history)}\n"
                   f"📅 Создан: {first_date_str} - {last_date_str}\n\n"
                   f"💡 Используйте этот файл для изучения языков в оффлайне!"
        )

        # Update main menu
        await callback.message.edit_text(
            "✅ PDF файл успешно создан и отправлен!",
            reply_markup=get_main_menu_keyboard(True)
        )

        await callback.answer("📄 PDF готов!")

    except Exception as e:
        logger.error(f"PDF export error: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании PDF файла.",
            reply_markup=get_main_menu_keyboard(True)
        )
        await callback.answer()

@router.callback_query(F.data == "export_txt")
async def export_txt_handler(callback: CallbackQuery):
    """Export history to TXT"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.answer("❌ Экспорт доступен только в премиум версии", show_alert=True)
        return

    # Show processing message
    await callback.message.edit_text("📝 Генерирую TXT файл...")

    try:
        # Get user's translation history
        history = await db.get_user_history(callback.from_user.id, limit=100)

        if not history:
            await callback.message.edit_text(
                "📝 История переводов пуста. Сначала сделайте несколько переводов.",
                reply_markup=get_main_menu_keyboard(True)
            )
            return

        # Generate TXT
        txt_data = await export_service.export_history_to_txt(callback.from_user.id, history)

        if not txt_data:
            await callback.message.edit_text(
                "❌ Ошибка при создании TXT файла. Попробуйте позже.",
                reply_markup=get_main_menu_keyboard(True)
            )
            return

        # Generate filename
        filename = await export_service.generate_export_filename(callback.from_user.id, 'txt')

        # Create file for sending
        txt_file = BufferedInputFile(txt_data, filename=filename)

        # Send TXT file
        from datetime import datetime
        first_date = history[0]['created_at']
        last_date = history[-1]['created_at']
        first_date_str = first_date.strftime('%Y-%m-%d') if isinstance(first_date, datetime) else first_date[:10]
        last_date_str = last_date.strftime('%Y-%m-%d') if isinstance(last_date, datetime) else last_date[:10]

        await callback.message.answer_document(
            txt_file,
            caption=f"📝 Ваш разговорник в текстовом формате\n\n"
                   f"📊 Переводов: {len(history)}\n"
                   f"📅 Создан: {first_date_str} - {last_date_str}\n\n"
                   f"💡 Простой формат для чтения в любом текстовом редакторе!"
        )

        # Update main menu
        await callback.message.edit_text(
            "✅ TXT файл успешно создан и отправлен!",
            reply_markup=get_main_menu_keyboard(True)
        )

        await callback.answer("📝 TXT готов!")

    except Exception as e:
        logger.error(f"TXT export error: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при создании TXT файла.",
            reply_markup=get_main_menu_keyboard(True)
        )
        await callback.answer()

@router.callback_query(F.data == "export_format")
async def export_format_handler(callback: CallbackQuery):
    """Show export format selection"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.answer("❌ Экспорт доступен только в премиум версии", show_alert=True)
        return

    await callback.message.edit_text(
        "📄 Выберите формат экспорта:\n\n"
        "• **PDF** - красиво оформленный документ с таблицами и статистикой\n"
        "• **TXT** - простой текстовый файл для любых устройств",
        reply_markup=get_export_format_keyboard(),
        parse_mode='Markdown'
    )
    await callback.answer()