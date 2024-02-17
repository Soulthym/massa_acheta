from loguru import logger

import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.formatting import as_list, as_line, TextLink, Code
from aiogram.enums import ParseMode

import app_globals
from remotes.node import check_node
from tools import get_short_address, save_app_results, check_privacy


class NodeAdder(StatesGroup):
    waiting_node_name = State()
    waiting_node_url = State()


router = Router()


@router.message(StateFilter(None), Command("add_node"))
@logger.catch
async def cmd_add_node(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
    if not await check_privacy(message=message): return
    
    t = as_list(
        "❓ Please enter a short name for the new node (nickname) or /cancel to quit the scenario:",
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await state.set_state(NodeAdder.waiting_node_name)
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(NodeAdder.waiting_node_name, F.text)
@logger.catch
async def input_nodename_to_add(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
    if not await check_privacy(message=message): return

    node_name = message.text
    await state.set_data(data={"node_name": node_name})

    if node_name in app_globals.app_results:
        t = as_list(
            f"‼ Error: Node with nickname \"{node_name}\" already exists", "",
            "👉 Try /add_node to add another node or /help to learn bot commands"
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

        await state.clear()
        return


    t = as_list(
        f"❓ Please enter API URL for the new node \"{node_name}\" with leading \"http(s)://...\" prefix or /cancel to quit the scenario: ", "",
        "💭 Typically API URL looks like: http://ip.ad.dre.ss:33035/api/v2"
    )
    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
        await state.set_state(NodeAdder.waiting_node_url)
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
        await state.clear()

    return



@router.message(NodeAdder.waiting_node_url, F.text.startswith("http"))
@logger.catch
async def add_node(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")
    if not await check_privacy(message=message): return

    user_state = await state.get_data()
    node_name = user_state['node_name']
    node_url = message.text
    await state.set_data(data={"node_url": node_url})

    try:
        async with app_globals.results_lock:
            app_globals.app_results[node_name] = {}
            app_globals.app_results[node_name]['url'] = node_url
            app_globals.app_results[node_name]['last_status'] = "unknown"
            app_globals.app_results[node_name]['last_update'] = 0
            app_globals.app_results[node_name]['last_result'] = {"unknown": "Never updated before"}
            app_globals.app_results[node_name]['wallets'] = {}
            await save_app_results()

    except BaseException as E:
        logger.error(f"Cannot add node '{node_name}' with URL '{node_url}': ({str(E)})")
        t = as_list(
            as_line(
                "‼ Error: Could not add node ",
                Code(get_short_address(node_name)),
                f" with API URL {node_url}"
            ),
            as_line(
                "💻 Result: ",
                Code(str(E))
            ),
            as_line(
                "⚠ Try again later or watch logs to check the reason - ",
                TextLink(
                    "More info here",
                    url="https://github.com/dex2code/massa_acheta/"
                )
            )
        )

    else:
        logger.info(f"Successfully added node '{node_name}' with URL '{node_url}'")
        t = as_list(
            as_line(
                "✅ Successfully added node: ",
                Code(get_short_address(node_name)),
                f" with API URL: {node_url}"
            ),
            "👁 You can check new settings using /view_config command", "",
            "☝ Please note that bot will update info for this node a bit later", "",
            "⚠ Please also check if you opened a firewall on the MASSA host:",
            as_line(
                "Use ",
                Code("sudo ufw allow 33035/tcp"),
                " command on Ubuntu hosts"
            )
        )

    try:
        await message.reply(
            text=t.as_html(),
            parse_mode=ParseMode.HTML,
            request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
        )
    except BaseException as E:
        logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    await state.clear()

    if app_globals.app_results[node_name]['last_status'] != True:
        async with app_globals.results_lock:
            await asyncio.gather(check_node(node_name=node_name))

    return
