import time
import curses
import curses.textpad
import curses.ascii
from typing import Tuple, List
from tcpsockets import client, logger
import textwrap

log_file = open("Log.txt", "a")
logger.set_log_files([log_file])

chats: List[str] = []
send_this: List[str] = []
running = True


def center(screen: curses.window) -> Tuple[int, int]:
    h, w = screen.getmaxyx()
    return h // 2, w // 2


def start(screen: curses.window):
    while 1:

        key = screen.getch()
        screen.erase()
        h_h, h_w = center(screen)
        head_text = "Potato Messenger"
        head = (h_h // 2, h_w - len(head_text) // 2, head_text)
        click_text = "Click Here To Continue or press Enter."
        button = (h_h, h_w - len(click_text) // 2, click_text)
        box1 = screen.subwin(3, len(button[2]) + 4, button[0] - 1, button[1] - 2)
        box1.box()
        screen.addstr(head[0], head[1], head[2])
        screen.addstr(button[0], button[1], button[2])
        if key == curses.KEY_ENTER or key in (10, 13):
            break
        if key == curses.KEY_MOUSE:
            _, mx, my, *_ = curses.getmouse()
            if button[1] <= mx <= button[1] + len(button[2]) and my == button[0]:
                break
        screen.refresh()
        time.sleep(1 / 10)


def chat_page(screen: curses.window):
    global running
    user_typing = False
    read_str = ""
    rendered_display_chats = 0
    display_chats: List[str] = []
    while running:
        key = screen.getch()
        if key == curses.KEY_MOUSE:
            _, mx, my, *_ = curses.getmouse()
            if my == center(screen)[0] * 2 - 2:
                user_typing = True
            else:
                user_typing = False
        elif key == 27 or key == curses.KEY_BREAK:
            running = False
        screen.erase()
        start_index = -1
        end_index = -(center(screen)[0] * 2 - 3) - 1
        box2 = screen.subwin(3, center(screen)[1] * 2, center(screen)[0] * 2 - 3, 0)
        box2.box()

        start_render_from = rendered_display_chats
        rendered_display_chats = len(chats)
        width_limit = center(screen)[1] * 2 - 2
        for chat in chats[start_render_from:]:
            parts = textwrap.fill(chat, width_limit).split("\n")
            display_chats.extend(parts)
        for index, msg in enumerate(display_chats[start_index:end_index:-1]):
            y = center(screen)[0] * 2 - 4 - index
            x = 0
            screen.addstr(y, x, msg)
        if user_typing:
            curses.curs_set(1)
            screen.move(center(screen)[0] * 2 - 2, len(read_str[-(center(screen)[1] - 2) * 2:]))
            if key:
                if key == curses.KEY_ENTER or key in (10, 13):
                    if read_str:
                        send_this.append(read_str)
                        read_str = ""
                elif key == curses.KEY_BACKSPACE or key == 8:
                    if read_str:
                        read_str = read_str[:-1]
                else:
                    if curses.ascii.isascii(key):
                        letter = chr(key)
                        read_str += letter
            screen.move(center(screen)[0] * 2 - 2, len(read_str[-(center(screen)[1] - 2) * 2:]))
        else:
            screen.move(0, center(screen)[1] * 2 - 1)
            if key == ord("q"):
                running = False
            elif key == ord("w") or key == curses.KEY_ENTER or key in (10, 18):
                user_typing = True
        screen.addstr(center(screen)[0] * 2 - 2, 1, read_str[-(center(screen)[1] - 2) * 2 - 1:])
        screen.refresh()


chat_srvr = client.ConnectedServer("192.168.56.1", 1234)


@chat_srvr.on_connection
def on_connection():
    global chats
    global running
    try:
        while running:
            if send_this:
                chat_srvr.send("POST")
                chat_srvr.send(send_this)
                send_this.clear()
            chat_srvr.send("GET")
            chats = chat_srvr.receive()
        chat_srvr.send("QUIT")
    except ConnectionResetError:
        running = False
        print("Server disconnected")


chat_srvr.connect()


@curses.wrapper
def main(screen: curses.window):
    curses.mousemask(1)
    screen.nodelay(1)
    curses.curs_set(0)
    start(screen)
    chat_page(screen)
