import asyncio
import json
import threading
from threading import Thread
from typing import List

import websockets

from location_cloaking.config import LocationServerConfig
from location_cloaking.location_server.model.messages import MsgLSClientInitComplete, MsgLSObserverIncUpd
from location_cloaking.model.data import GranularityLevel
from location_cloaking.model.messages import MsgClientLSInit
from location_cloaking.visualizer import viz
from location_cloaking.visualizer.model.data import VisualizeEntry

entries: List[VisualizeEntry] = []
granules = []


async def threaded_function():
    uri = f"ws://127.0.0.1:{LocationServerConfig.LISTEN_PORT}"
    async with websockets.connect(uri) as websocket:
        await websocket.send(MsgClientLSInit(
            mode="observer",
            alias=[]
        ).to_json())
        message = await websocket.recv()

        init_response = MsgLSClientInitComplete.from_json(message)
        while True:
            message = await websocket.recv()
            event = json.loads(message)
            if event["type"] == "MsgLSObserverIncUpd":
                upd = MsgLSObserverIncUpd.from_json(message)
                print(upd)
                # global granules
                global entries
                entry_alias_list = list(set([alias for e in entries for alias in e.alias]))
                # print(entry_alias_list)
                if not entry_alias_list or set(entry_alias_list).isdisjoint(upd.alias):
                    entry = VisualizeEntry(
                        alias=upd.alias,
                        color=(119, 136, 153),
                        granularities=[GranularityLevel(
                            upd.new_location,
                            upd.vicinity_insert
                        )],
                        vicinity_shape=upd.vicinity_shape,
                        level=upd.level
                    )
                    entries.append(entry)
                else:
                    entry_list = [e for e in entries if not set(e.alias).isdisjoint(upd.alias)]
                    for entry in entry_list:
                        del entry.granularities[upd.level + 1:]
                        if upd.level == len(entry.granularities):
                            entry.granularities.append(GranularityLevel(
                                    upd.new_location,
                                    upd.vicinity_insert
                            ))
                        else:
                            level_vicinity = entry.granularities[upd.level].vicinity

                            entry.granularities[upd.level].location = upd.new_location
                            entry.granularities[upd.level].vicinity.granules = [g for g in level_vicinity.granules if g not in upd.vicinity_delete.granules]
                            entry.granularities[upd.level].vicinity.granules.extend(upd.vicinity_insert.granules)

                        entry.level = max(0, len(entry.granularities) - 1)

def a():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(threaded_function())

def main():
    global entries
    thread = Thread(target=a, args=())
    thread.daemon = True
    thread.start()

    print("ok")
    viz.main(entries)
    thread.join()
    pass

if __name__ == '__main__':
    main()
