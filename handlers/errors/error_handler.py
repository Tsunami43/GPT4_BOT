import html
import logging

from aiogram import types

from loader import dp, exceptions_chat_id


@dp.errors_handler()
async def errors_handler(update:types.Update, exception :KeyError):

    chat_id = None

    state = dp.current_state()
    await state.reset_state(with_data=True)

    if update.callback_query:
        user = update.callback_query.from_user
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        user = update.message.from_user
        chat_id= update.message.chat.id


    if chat_id:
        await dp.bot.send_message(chat_id=exceptions_chat_id, text=f'Виникла помилка у {user.get_mention(as_html=True)}:\n\n{html.escape(exception.__str__())}\n\n{html.escape(update.__str__())}')

    logging.exception(f'Update: {update} \n{exception}')
    return True

# @dp.errors_handler()
# async def errors_handler(update, exception):
#     """
#     Exceptions handler. Catches all exceptions within task factory tasks.
#     :param update:
#     :param exception:
#     :return: stdout logging
#     """
#     from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
#                                           CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
#                                           MessageTextIsEmpty, RetryAfter,
#                                           CantParseEntities, MessageCantBeDeleted, BadRequest)
#
#     if isinstance(exception, CantDemoteChatCreator):
#         logging.debug("Can't demote chat creator")
#         return True
#
#     if isinstance(exception, MessageNotModified):
#         logging.debug('Message is not modified')
#         return True
#     if isinstance(exception, MessageCantBeDeleted):
#         logging.debug('Message cant be deleted')
#         return True
#
#     if isinstance(exception, MessageToDeleteNotFound):
#         logging.debug('Message to delete not found')
#         return True
#
#     if isinstance(exception, MessageTextIsEmpty):
#         logging.debug('MessageTextIsEmpty')
#         return True
#
#     if isinstance(exception, Unauthorized):
#         logging.info(f'Unauthorized: {exception}')
#         return True
#
#     if isinstance(exception, InvalidQueryID):
#         logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
#         return True
#
#     if isinstance(exception, TelegramAPIError):
#         logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, RetryAfter):
#         logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, CantParseEntities):
#         logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
#         return True
#     if isinstance(exception, BadRequest):
#         logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
#         return True
#     logging.exception(f'Update: {update} \n{exception}')
