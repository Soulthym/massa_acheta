from loguru import logger

from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line
from aiogram.enums import ParseMode
from quickchart import QuickChart

from app_config import app_config
import app_globals


router = Router()


@router.message(StateFilter(None), Command("massa_chart"))
@logger.catch
async def cmd_massa_chart(message: Message) -> None:
    logger.debug("-> Enter Def")
    logger.info(f"-> Got '{message.text}' command from '{message.from_user.id}'@'{message.chat.id}'")

    chart_config = {
        "type": "line",

        "options": {

            "title": {
                "display": True,
                "text": "MASSA Mainnet chart"
            },

            "scales": {
                "yAxes": [
                    {
                        "id": "stakers",
                        "display": True,
                        "position": "left",
                        "ticks": { "fontColor": "Teal" },
                        "gridLines": { "drawOnChartArea": False }
                    },
                    {
                        "id": "rolls",
                        "display": True,
                        "position": "right",
                        "ticks": { "fontColor": "FireBrick" },
                        "gridLines": { "drawOnChartArea": True }
                    }
                ]
            }
        },

        "data": {
            "labels": [],

            "datasets": [
                {
                    "label": "Active stakers",
                    "yAxisID": "stakers",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "Teal",
                    "borderWidth": 2,
                    "pointRadius": 2,
                    "data": []
                },
                {
                    "label": "Rolls staked",
                    "yAxisID": "rolls",
                    "lineTension": 0.4,
                    "fill": False,
                    "borderColor": "FireBrick",
                    "borderWidth": 2,
                    "pointRadius": 2,
                    "data": []
                }
            ]
        }
    }

    try:
        massa_stat_keytime_unsorted = {}
        for measure in app_globals.massa_network['stat']:
            measure_time = measure['time']
            measure_cycle = measure['cycle']
            measure_stakers = measure['stakers']
            measure_rolls = measure['rolls']

            massa_stat_keytime_unsorted[measure_time] = {
                "cycle": measure_cycle,
                "stakers": measure_stakers,
                "rolls": measure_rolls
            }

        massa_stat_keytime_sorted = dict(
            sorted(
                massa_stat_keytime_unsorted.items()
            )
        )

        massa_stat_keycycle_unsorted = {}
        for measure in massa_stat_keytime_sorted:
            measure_cycle = massa_stat_keytime_sorted[measure]['cycle']
            measure_stakers = massa_stat_keytime_sorted[measure]['stakers']
            measure_rolls = massa_stat_keytime_sorted[measure]['rolls']

            massa_stat_keycycle_unsorted[measure_cycle] = {
                "stakers": measure_stakers,
                "rolls": measure_rolls
            }

        massa_stat_keycycle_sorted = dict(
            sorted(
                massa_stat_keycycle_unsorted.items()
            )
        )

        for cycle in massa_stat_keycycle_sorted:
            stakers = massa_stat_keycycle_sorted[cycle]['stakers']
            rolls = massa_stat_keycycle_sorted[cycle]['rolls']

            chart_config['data']['labels'].append(cycle)
            chart_config['data']['datasets'][0]['data'].append(stakers)
            chart_config['data']['datasets'][1]['data'].append(rolls)

        chart = QuickChart()
        chart.device_pixel_ratio = 2.0
        chart.width = 600
        chart.height = 300
        chart.config = chart_config
        chart_url = chart.get_url()

    except BaseException as E:
        logger.error(f"Cannot prepare MASSA Mainnet chart ({str(E)})")
        t = as_list(
            as_line("🤷 Charts are temporary unavailable. Try later."),
            as_line("☝ Use /help to learn bot commands")
        )
        try:
            await message.reply(
                text=t.as_html(),
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    else:
        try:
            await message.reply_photo(
                photo=chart_url,
                parse_mode=ParseMode.HTML,
                request_timeout=app_config['telegram']['sending_timeout_sec']
            )
        except BaseException as E:
            logger.error(f"Could not send message to user '{message.from_user.id}' in chat '{message.chat.id}' ({str(E)})")

    return
