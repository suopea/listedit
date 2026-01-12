import curses
import os
import sys

pad_left = 4
pad_bottom = 7
min_size = 6


def main(w):
    things = []
    if len(sys.argv) > 2:
        print("too many arguments")
        quit()
    if len(sys.argv) == 1:
        filename = ask_for_filename()
    else:
        filename = sys.argv[1]
    with open(filename) as file:
        for line in file.readlines():
            if line != "\n":
                things.append(line[:-1])
    query = ""
    while True:
        query = get_query(w, things, query)
        query = if_enter_apply_query(w, query, things, filename)


def if_enter_apply_query(w, query, things, filename):
    if query and query[-1] == "\n" and query != "\n":
        query = query[:-1]
        query = apply_query(w, query, things, filename)
    return query


def get_query(w, things, query):
    query_y = 2
    results_y = 4
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
        print_results(w, 4, things, query)
    elif key == "\n" and query == "":
        pass
    else:
        query += key
    return query


def ask_for_filename():
    files = [f for f in os.listdir('.')]

    return "testfile"


def apply_query(w, query, things, filename):
    if query in "quit":
        save_and_quit(w, things, filename)
    elif query in "undo":
        query = things.pop()
        w.addstr(2, pad_left + len(query) + 1,
                 "deleted. Press enter to add back")
        return query
    elif query in things:
        key = "key"
        while key not in "yn":
            w.clear()
            w.addstr(2, pad_left, f"delete {query}, y/n?")
            key = w.getkey()
        if key == "y":
            things.remove(query)
            w.clear()
            w.addstr(2, pad_left, f"{query} removed. Press enter to add back")
    else:
        things.append(query)
        w.clear()
        w.addstr(2, pad_left, f"{query} added. Enter 'undo' to undo")
        return ""


def save_and_quit(w, things, filename):
    key = "key"
    while key not in "yn":
        w.clear()
        w.addstr(2, pad_left, f"save to {filename}, y/n?")
        key = w.getkey()
    if key == "y":
        write_out(filename, things)
        w.clear()
        w.addstr(2, pad_left, "saved! press any key...")
    else:
        w.clear()
        w.addstr(2, pad_left, "not saved. press any key...")
    key = w.getkey()
    quit()


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
