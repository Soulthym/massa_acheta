from loguru import logger

import json
from time import time as t_now
from aiogram.utils.formatting import as_list, as_line, Code, TextLink

import app_globals
from telegram.queue import queue_telegram_message
from tools import pull_node_api, get_short_address


@logger.catch
async def check_wallet(node_name: str="", wallet_addr: str="") -> None:
    logger.debug(f"-> Enter Def")

    if app_globals.app_results[node_name]['last_status'] != True:
        logger.warning(f"Will not watch wallet '{wallet_addr}' on node '{node_name}' because of its offline")
        return

    payload = json.dumps({
        "id": 0,
        "jsonrpc": "2.0",
        "method": "get_addresses",
        "params": [[wallet_addr]]
    })

    try:
        wallet_response = await pull_node_api(api_url=app_globals.app_results[node_name]['url'], api_payload=payload)
        wallet_result = wallet_response[0]

        wallet_final_balance = round(float(wallet_result['final_balance']), 4)
        wallet_candidate_rolls = int(wallet_result['candidate_roll_count'])

        if type(wallet_result['cycle_infos'][-1]['active_rolls']) == int:
            wallet_active_rolls = int(wallet_result['cycle_infos'][-1]['active_rolls'])
        else:
            wallet_active_rolls = 0

        wallet_missed_blocks = 0
        for cycle_info in wallet_result['cycle_infos']:
            if type(cycle_info['nok_count']) == int:
                wallet_missed_blocks += int(cycle_info['nok_count'])

        wallet_last_cycle_missed_blocks = int(wallet_result['cycle_infos'][-1]['nok_count'])

    except Exception as E:
        logger.warning(f"Error watching wallet '{wallet_addr}' on '{node_name}': ({str(E)})")

        if app_globals.app_results[node_name]['wallets'][wallet_addr]['last_status'] != False:
            t = as_list(
                as_line(f"🏠 Node: ", Code(node_name), end=""),
                as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                as_line(
                    "🚨 Cannot get info for wallet: ",
                    TextLink(
                        get_short_address(address=wallet_addr),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                    )
                ),
                as_line("💻 Result: ", Code(wallet_response)),
                "⚠ Check wallet address or node settings!"
            )
            await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['wallets'][wallet_addr]['last_status'] = False
        app_globals.app_results[node_name]['wallets'][wallet_addr]['last_result'] = wallet_response

    else:
        logger.info(f"Got wallet '{wallet_addr}' on node '{node_name}' info successfully!")

        if app_globals.app_results[node_name]['wallets'][wallet_addr]['last_status'] != True:
            t = as_list(
                as_line(f"🏠 Node: ", Code(node_name), end=""),
                as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                as_line(
                    "👛 Successfully got info for wallet: ",
                    TextLink(
                        get_short_address(address=wallet_addr),
                        url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                    )
                ),
                as_line(
                    "💰 Final balance: ",
                    Code(wallet_final_balance),
                    " MASSA",
                    end=""
                ),
                f"🧻 Candidate/Active rolls: {wallet_candidate_rolls}/{wallet_active_rolls}",
                f"🥊 Missed blocks: {wallet_missed_blocks}"
            )
            await queue_telegram_message(message_text=t.as_html())

        else:

            # 1) Check if balance is decreased:
            if wallet_final_balance < app_globals.app_results[node_name]['wallets'][wallet_addr]['final_balance']:
                t = as_list(
                    as_line(f"🏠 Node: ", Code(node_name), end=""),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "💸 Decreased balance on wallet: ",
                        TextLink(
                            get_short_address(address=wallet_addr),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                        )
                    ),
                    as_line(
                        "👁 New final balance: ",
                        Code(app_globals.app_results[node_name]['wallets'][wallet_addr]['final_balance']),
                        " → ",
                        Code(wallet_final_balance),
                        " MASSA"
                    )
                )
                await queue_telegram_message(message_text=t.as_html())

            # 2) Check if candidate rolls changed:
            if wallet_candidate_rolls != app_globals.app_results[node_name]['wallets'][wallet_addr]['candidate_rolls']:
                t = as_list(
                    as_line(f"🏠 Node: ", Code(node_name), end=""),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "🧻 Candidate rolls changed on wallet:",
                        TextLink(
                            get_short_address(address=wallet_addr),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                        )
                    ),
                    as_line(
                        "👁 New candidate rolls number: ",
                        Code(app_globals.app_results[node_name]['wallets'][wallet_addr]['candidate_rolls']),
                        " → ",
                        Code(wallet_candidate_rolls)
                    )
                )
                await queue_telegram_message(message_text=t.as_html())

            # 3) Check if active rolls changed:
            if wallet_active_rolls != app_globals.app_results[node_name]['wallets'][wallet_addr]['active_rolls']:
                t = as_list(
                    as_line(f"🏠 Node: ", Code(node_name), end=""),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "🧻 Active rolls changed on wallet:",
                        TextLink(
                            get_short_address(address=wallet_addr),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                        )
                    ),
                    as_line(
                        "👁 New active rolls number: ",
                        Code(app_globals.app_results[node_name]['wallets'][wallet_addr]['active_rolls']),
                        " → ",
                        Code(wallet_active_rolls)
                    )
                )
                await queue_telegram_message(message_text=t.as_html())

            # 4) Check if new blocks missed:
            if wallet_missed_blocks > app_globals.app_results[node_name]['wallets'][wallet_addr]['missed_blocks']:
                t = as_list(
                    as_line(f"🏠 Node: ", Code(node_name), end=""),
                    as_line(f"📍 {app_globals.app_results[node_name]['url']}"),
                    as_line(
                        "🥊 New missed blocks on wallet:",
                        TextLink(
                            get_short_address(address=wallet_addr),
                            url=f"{app_globals.app_config['service']['mainnet_explorer']}/address/{wallet_addr}"
                        )
                    ),
                    as_line(
                        "👁 Blocks missed in last cycle: ",
                        Code(wallet_last_cycle_missed_blocks)
                    )
                )
                await queue_telegram_message(message_text=t.as_html())

        app_globals.app_results[node_name]['wallets'][wallet_addr]['last_status'] = True
        app_globals.app_results[node_name]['wallets'][wallet_addr]['last_update'] = t_now()

        app_globals.app_results[node_name]['wallets'][wallet_addr]['final_balance'] = wallet_final_balance
        app_globals.app_results[node_name]['wallets'][wallet_addr]['candidate_rolls'] = wallet_candidate_rolls
        app_globals.app_results[node_name]['wallets'][wallet_addr]['active_rolls'] = wallet_active_rolls
        app_globals.app_results[node_name]['wallets'][wallet_addr]['missed_blocks'] = wallet_missed_blocks

        app_globals.app_results[node_name]['wallets'][wallet_addr]['last_result'] = wallet_result

    finally:
        logger.debug(f"API result for wallet '{wallet_addr}' on node '{node_name}':\n{json.dumps(obj=app_globals.app_results[node_name]['wallets'][wallet_addr]['last_result'], indent=4)}")


    return




if __name__ == "__main__":
    pass
