from loguru import logger

import json
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.utils.formatting import as_list, as_line, Code, TextLink, Underline, Text
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


import app_globals
from tools import pull_http_api, get_short_address


class AddressViewer(StatesGroup):
    waiting_wallet_address = State()

router = Router()


@logger.catch
async def get_address(wallet_address: str="") -> Text:
    logger.debug("-> Enter Def")

    if not wallet_address.startswith("AU"):
        return as_list(
            "‼ Wrong wallet address format (expected a string starting with AU prefix)", "",
            as_line(
                "☝ Try /view_address with ",
                Underline("AU..."),
                " wallet address"
            )
        )

    payload = json.dumps(
        {
            "id": 0,
            "jsonrpc": "2.0",
            "method": "get_addresses",
            "params": [[wallet_address]]
        }
    )

    try:
        wallet_answer = await pull_http_api(api_url=app_globals.app_config['service']['mainnet_rpc_url'],
                                            api_method="POST",
                                            api_payload=payload,
                                            api_root_element="result")

        wallet_result = wallet_answer.get("result", None)
        if not wallet_result:
            raise Exception(f"Wrong answer from MASSA node API ({str(wallet_answer)})")

        if type(wallet_result) != list or not len(wallet_result):
            raise Exception(f"Wrong answer from MASSA node API ({str(wallet_answer)})")

        wallet_result = wallet_result[0]

        wallet_result_address = wallet_result.get("address", None)
        if wallet_result_address != wallet_address:
            raise Exception(f"Bad address received from MASSA node API: '{wallet_result_address}' (expected '{wallet_address}')")

    except BaseException as E:
        logger.warning(f"Cannot operate received address result: ({str(E)})")

        return as_list(
            as_line(
                "👛 Wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                )
            ),
            as_line(
                "⁉ Error getting address info for wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                )
            ),
            as_line(
                "💥 Exception: ",
                Code(str(E))
            ),
            as_line("⚠️ Check wallet address or try later!")
        )

    else:
        logger.info(f"Successfully received result for address '{wallet_address}'")

        wallet_final_balance = 0
        wallet_final_balance = wallet_result.get("final_balance", 0)
        wallet_final_balance = float(wallet_final_balance)
        wallet_final_balance = round(wallet_final_balance, 4)

        wallet_candidate_rolls = 0
        wallet_candidate_rolls = wallet_result.get("candidate_roll_count", 0)
        wallet_candidate_rolls = int(wallet_candidate_rolls)

        wallet_active_rolls = 0
        if type(wallet_result['cycle_infos'][-1].get("active_rolls", 0)) == int:
            wallet_active_rolls = wallet_result['cycle_infos'][-1].get("active_rolls", 0)

        wallet_missed_blocks = 0
        for cycle_info in wallet_result.get("cycle_infos", []):
            if type(cycle_info.get("nok_count", 0)) == int:
                wallet_missed_blocks += cycle_info.get("nok_count", 0)

        wallet_computed_rewards = ""
        if (app_globals.massa_network_values['total_staked_rolls'] > 0) and (app_globals.massa_network_values['block_reward'] > 0) and (wallet_active_rolls > 0):
            my_contribution = app_globals.massa_network_values['total_staked_rolls'] / wallet_active_rolls
            my_blocks = 172_800 / my_contribution
            my_reward = round(
                my_blocks * app_globals.massa_network_values['block_reward'],
                2
            )
            wallet_computed_rewards = f"\n🪙 Possible MAX reward ≈ {my_reward:,} MAS / day\n"

        wallet_thread = wallet_result.get("thread", 0)

        cycles_list = []
        wallet_cycles = wallet_result.get("cycle_infos", [])

        if len(wallet_cycles) == 0:
            cycles_list.append("🌀 Cycles info: No data")
        else:
            cycles_list.append("🌀 Cycles info (Produced / Missed):")
            for wallet_cycle in wallet_cycles:
                cycle_num = wallet_cycle.get("cycle", 0)
                ok_count = wallet_cycle.get("ok_count", 0)
                nok_count = wallet_cycle.get("nok_count", 0)
                cycles_list.append(f" ⋅ Cycle {cycle_num}: ( {ok_count} / {nok_count} )")
        

        credit_list = []
        wallet_credits = wallet_result.get("deferred_credits", [])

        if len(wallet_credits) == 0:
            credit_list.append("💳 Deferred credits: No data")

        else:
            credit_list.append("💳 Deferred credits: ")

            for wallet_credit in wallet_credits:
                credit_amount = round(
                    float(wallet_credit['amount']),
                    4
                )

                credit_period = int(wallet_credit['slot']['period'])
                credit_unix = 1705312800 + (credit_period * 16)
                credit_date = datetime.utcfromtimestamp(credit_unix).strftime("%b %d, %Y")

                credit_list.append(
                    f" ⋅ {credit_date}: {credit_amount:,} MAS"
                )

        return as_list(
            as_line(
                "👛 Wallet: ",
                TextLink(
                    get_short_address(wallet_address),
                    url=f"{app_globals.app_config['service']['mainnet_explorer_url']}/address/{wallet_address}"
                )
            ),
            f"💰 Final balance: {wallet_final_balance:,} MAS",
            f"🗞 Candidate / Active rolls: {wallet_candidate_rolls:,} / {wallet_active_rolls:,}",
            f"🥊 Missed blocks: {wallet_missed_blocks}",
            wallet_computed_rewards,
            "🔎 Detailed info:", "",
            f"🧵 Thread: {wallet_thread}", "",
            *cycles_list, "",
            *credit_list, "",
            "☝ To view ALL deferred credits try /view_credits command"
        )



@router.message(StateFilter(None), Command("view_address"))
@logger.catch
async def cmd_view_address(message: Message, state: FSMContext) -> None:
    logger.debug("->Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    message_list = message.text.split()
    if len(message_list) < 2:
        t = as_list(
            "❓ Please answer with a wallet address you want to explore: ", "",
            as_line(
                "☝ The wallet address must start with ",
                Underline("AU"),
                " prefix"
            ),
            "👉 Use /cancel to quit the scenario"

        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_globals.app_config['telegram']['sending_timeout_sec']
            )
            await state.set_state(AddressViewer.waiting_wallet_address)
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")
            await state.clear()

        return

    wallet_address = message_list[1]
    t = await get_address(wallet_address=wallet_address)
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



@router.message(AddressViewer.waiting_wallet_address, F.text)
@logger.catch
async def show_address(message: Message, state: FSMContext) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from user '{message.from_user.id}' in chat '{message.chat.id}'")

    wallet_address = ""
    command_list = message.text.split()
    for cmd in command_list:
        if cmd.startswith("AU"):
            wallet_address = cmd
            break

    t = await get_address(wallet_address=wallet_address)
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
