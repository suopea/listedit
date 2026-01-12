import curses
import string
import os
import sys
from copy import deepcopy

pad_left = 4
pad_bottom = 7
min_size = 6
query_y = 2
results_y = 4


def main(w):
    if len(sys.argv) > 2:
        print("give one or none files as arguments")
        quit()
    if len(sys.argv) == 1:
        filename = ask_for_filename(w)
    else:
        filename = sys.argv[1]
    things = []
    with open(filename) as file:
        for line in file.readlines():
            if not just_whitespace(line):
                things.append(line[:-1])
    things_at_start = deepcopy(things)
    query = ""
    while True:
        query = get_query(w, things, query)
        if just_whitespace(query):
            pass
        elif query in things:
            tooltip(w, query, "DELETE from list")
        elif completes_to(query, "quit"):
            tooltip(w, query, "QUIT (and save if you want)")
        elif completes_to(query, "undo"):
            tooltip(w, query, f"REMOVE or edit {things[-1].upper()}")
        elif query:
            tooltip(w, query, "ADD to list")
        query = if_enter_apply_query(
            w, query, things, things_at_start, filename)


def completes_to(a, b):
    return a == b[:len(a)]


def if_enter_apply_query(w, query, things, things_at_start, filename):
    if query and query[-1] == "\n" and query != "\n":
        query = query[:-1]
        query = apply_query(w, query, things, things_at_start, filename)
    return query


def just_whitespace(thing):
    for c in thing:
        if c not in string.whitespace:
            return False
    return True


def get_query(w, things, query):
    while height(w) < min_size or width(w) < min_size:
        w.clear()
        w.getkey()
    print_results(w, results_y, things, query)
    w.addstr(query_y, pad_left, query)
    key = w.getkey()
    w.clear()
    if key == "KEY_BACKSPACE":
        query = query[:-1]
    elif key == "KEY_RESIZE":
        w.clear()
        print_results(w, results_y, things, query)
    elif key == "\n" and query == "":
        pass
    elif key == "\t":
        query = tab_complete(things, query)
    elif key == "KEY_DOWN" or key == "KEY_UP":
        query = ""
    elif key in string.printable:
        query += key
    else:
        pass
    return query


def tab_complete(things, query):
    for thing in things[::-1]:
        if query in thing:
            return thing
    return query


def ask_for_filename(w):
    files = [f for f in os.listdir('.')]
    query = ""
    while True:
        if not query:
            tooltip(w, query, "give a filename to open or create")
        query = get_query(w, files, query)
        if query and query[-1] == "\n":
            query = query[:-1]
            if completes_to(query, "quit"):
                quit()
            elif query in files:
                if os.path.isfile(query):
                    return query
            else:
                with open(query, "w"):
                    pass
                return query
        if query in files:
            if os.path.isfile(query):
                tooltip(w, query, "OPEN file")
            else:
                tooltip(w, query, "is a directory")
        elif completes_to(query, "quit"):
            tooltip(w, query, "QUIT")
        else:
            tooltip(w, query, "CREATE file")


def tooltip(w, query, message):
    w.addstr(query_y, pad_left + len(query) + 2, message)


def apply_query(w, query, things, things_at_start, filename):
    if completes_to(query, "quit"):
        save_and_quit(w, things, things_at_start, filename)
        w.clear()
        return ""
    elif completes_to(query, "undo"):
        query = things.pop()
        tooltip(w, query, "deleted. Press enter to add back")
        return query
    elif query in things:
        things.remove(query)
        w.clear()
        tooltip(w, query, "removed. Press enter to add back")
        print_results(w, query_y, things, query)
        return query
    else:
        things.append(query)
        w.clear()
        tooltip(w, query, "added. Say 'undo' to undo")
        w.addstr(2, pad_left, f"{query} added. Enter 'undo' to undo")
        return ""


def save_and_quit(w, things, things_at_start, filename):
    key = "key"
    curses.curs_set(0)
    while key not in "ync":
        w.clear()
        w.addstr(2, pad_left, f"save to {filename}, y/n? (or c to go back)")
        print_changes(w, things, things_at_start, 4)
        key = w.getkey()
    if key == "y":
        write_out(filename, things)
        w.clear()
        w.addstr(2, pad_left, "saved! press any key...")
    elif key == "c":
        return
    else:
        w.clear()
        w.addstr(2, pad_left, "not saved. press any key...")
    w.getkey()
    quit()


def print_changes(w, things, things_at_start, line):
    if two_small_to_draw(w):
        return
    added = []
    removed = []
    for thing in things[::-1]:
        if thing not in things_at_start:
            added.append(thing)
    for thing in things_at_start[::-1]:
        if thing not in things:
            removed.append(thing)
    if not added and not removed:
        w.clear()
        w.addstr(query_y, pad_left, "no changes made, press any key to quit...")
        w.getkey()
        quit()
    if height(w) - line < 4:
        w.addstr(line + 1, pad_left, "...")
        return
    if added:
        w.addstr(line, pad_left, "added:")
        line += 2
    for thing in added:
        w.addstr(line, pad_left, thing)
        line += 1
    if height(w) - line < 4:
        w.addstr(line + 1, pad_left, "...")
        return
    line += 1
    if removed:
        w.addstr(line, pad_left, "removed:")
        line += 2
    for thing in removed:
        w.addstr(line, pad_left, thing)
        line += 1


def two_small_to_draw(w):
    return width(w) < 10 or height(w) < 6


def write_out(filename, things):
    with open(filename, "w") as file:
        for thing in things:
            file.write(thing)
            file.write("\n")


def width(w):
    return w.getmaxyx()[1]


def height(w):
    return w.getmaxyx()[0]


def print_results(w, startline, things, query):
    results = 0
    for thing in things[::-1]:
        if results > height(w) - pad_bottom:
            break
        if query in thing:
            w.addstr(startline + results, pad_left,
                     thing[:width(w) - pad_left])
            results += 1


curses.wrapper(main)
