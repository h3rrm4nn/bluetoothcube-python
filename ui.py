#!/usr/bin/python
# -*- coding: utf-8 -*-

import curses

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE,   curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_YELLOW,  curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_MAGENTA)
    curses.init_pair(4, curses.COLOR_RED,     curses.COLOR_RED)
    curses.init_pair(5, curses.COLOR_GREEN,   curses.COLOR_GREEN)
    curses.init_pair(6, curses.COLOR_BLUE,    curses.COLOR_BLUE)
    if curses.can_change_color():
        curses.init_color(7, 800, 800, 800) # White
        curses.init_color(3, 800, 800,   0) # Yellow
        curses.init_color(5, 800, 400,   0) # Orange (Magenta)
        curses.init_color(1, 800,   0,   0) # Red
        curses.init_color(2,   0, 800,   0) # Green
        curses.init_color(4,   0,   0, 800) # Blue

def draw_face(face):

    length = 4
    height = 2
    hspace = 1
    vspace = 1
    cube_pos = [4, 4]
    colors = {'W': 1, 'Y': 2, 'O': 3, 'R': 4, 'G': 5, 'B': 6}

    face_posx = 0
    face_posy = 0
    if face[1][1] == 'W':
        face_posx = 1
        face_posy = 1
    elif face[1][1] == 'O':
        face_posx = 0
        face_posy = 1
    elif face[1][1] == 'G':
        face_posx = 1
        face_posy = 2
    elif face[1][1] == 'R':
        face_posx = 2
        face_posy = 1
    elif face[1][1] == 'B':
        face_posx = 1
        face_posy = 0
    elif face[1][1] == 'Y':
        face_posx = 3
        face_posy = 1

    fspace = [3, 1]
    facex = face_posx * (3*(length+hspace) + fspace[0])+cube_pos[1]
    facey = face_posy * (3*(height+vspace) + fspace[1])+cube_pos[0]

    for i in range(3):
        for j in range(3):
            win = curses.newwin(height, length, facey + j*(height+vspace), facex + i*(length+hspace))
            win.bkgd(curses.color_pair(colors[face[j][i]]))
            win.refresh()


def draw_cube(state):

    corner = ['WRG', 'WGO', 'WOB', 'WBR', 'YGR', 'YOG', 'YBO', 'YRB']
    edge = ['WR', 'WG', 'WO', 'WB', 'YR', 'YG', 'YO', 'YB', 'RG', 'OG', 'OB', 'RB']

    A = corner[state[0][2]][(state[1][2])]
    B = corner[state[0][3]][(state[1][3])]
    C = corner[state[0][0]][(state[1][0])]
    D = corner[state[0][1]][(state[1][1])]

    E = corner[state[0][2]][(state[1][2]+1) % 3]
    F = corner[state[0][1]][(state[1][1]+2) % 3]
    G = corner[state[0][5]][(state[1][5]+1) % 3]
    H = corner[state[0][6]][(state[1][6]+2) % 3]

    I = corner[state[0][1]][(state[1][1]+1) % 3]
    J = corner[state[0][0]][(state[1][0]+2) % 3]
    K = corner[state[0][4]][(state[1][4]+1) % 3]
    L = corner[state[0][5]][(state[1][5]+2) % 3]

    M = corner[state[0][0]][(state[1][0]+1) % 3]
    N = corner[state[0][3]][(state[1][3]+2) % 3]
    O = corner[state[0][7]][(state[1][7]+1) % 3]
    P = corner[state[0][4]][(state[1][4]+2) % 3]

    Q = corner[state[0][3]][(state[1][3]+1) % 3]
    R = corner[state[0][2]][(state[1][2]+2) % 3]
    S = corner[state[0][6]][(state[1][6]+1) % 3]
    T = corner[state[0][7]][(state[1][7]+2) % 3]

    U = corner[state[0][6]][(state[1][6])]
    V = corner[state[0][7]][(state[1][7])]
    W = corner[state[0][4]][(state[1][4])]
    X = corner[state[0][5]][(state[1][5])]


    a = edge[state[2][3]][(state[3][3])]
    b = edge[state[2][0]][(state[3][0])]
    c = edge[state[2][1]][(state[3][1])]
    d = edge[state[2][2]][(state[3][2])]

    e = edge[state[2][ 2]][(state[3][ 2]+1) % 2]
    f = edge[state[2][ 9]][(state[3][ 9]+0) % 2]
    g = edge[state[2][ 6]][(state[3][ 6]+1) % 2]
    h = edge[state[2][10]][(state[3][10]+0) % 2]

    i = edge[state[2][1]][(state[3][1]+1) % 2]
    j = edge[state[2][8]][(state[3][8]+1) % 2]
    k = edge[state[2][5]][(state[3][5]+1) % 2]
    l = edge[state[2][9]][(state[3][9]+1) % 2]

    m = edge[state[2][ 0]][(state[3][ 0]+1) % 2]
    n = edge[state[2][11]][(state[3][11]+0) % 2]
    o = edge[state[2][ 4]][(state[3][ 4]+1) % 2]
    p = edge[state[2][ 8]][(state[3][ 8]+0) % 2]

    q = edge[state[2][ 3]][(state[3][ 3]+1) % 2]
    r = edge[state[2][10]][(state[3][10]+1) % 2]
    s = edge[state[2][ 7]][(state[3][ 7]+1) % 2]
    t = edge[state[2][11]][(state[3][11]+1) % 2]

    u = edge[state[2][6]][(state[3][6])]
    v = edge[state[2][7]][(state[3][7])]
    w = edge[state[2][4]][(state[3][4])]
    x = edge[state[2][5]][(state[3][5])]

    cube = [
        [
            [A,  a,  B],
            [d, 'W', b],
            [D,  c,  C],
        ],
        [
            [E,  e,  F],
            [h, 'O', f],
            [H,  g,  G],
        ],
        [
            [I,  i,  J],
            [l, 'G', j],
            [L,  k,  K],
        ],
        [
            [M,  m,  N],
            [p, 'R', n],
            [P,  o,  O],
        ],
        [
            [Q,  q,  R],
            [t, 'B', r],
            [T,  s,  S],
        ],
        [
            [U,  u,  V],
            [x, 'Y', v],
            [X,  w,  W],
        ],
    ]
    # cube = [
    #     [
    #         ['W', 'W', 'W'],
    #         ['W', 'W', 'W'],
    #         ['W', 'W', 'W'],
    #     ],
    #     [
    #         ['Y', 'Y', 'Y'],
    #         ['Y', 'Y', 'Y'],
    #         ['Y', 'Y', 'Y'],
    #     ],
    #     [
    #         ['O', 'O', 'O'],
    #         ['O', 'O', 'O'],
    #         ['O', 'O', 'O'],
    #     ],
    #     [
    #         ['R', 'R', 'R'],
    #         ['R', 'R', 'R'],
    #         ['R', 'R', 'R'],
    #     ],
    #     [
    #         ['G', 'G', 'G'],
    #         ['G', 'G', 'G'],
    #         ['G', 'G', 'G'],
    #     ],
    #     [
    #         ['B', 'B', 'B'],
    #         ['B', 'B', 'B'],
    #         ['B', 'B', 'B'],
    #     ],
    # ]
    draw_face(cube[0])
    draw_face(cube[1])
    draw_face(cube[2])
    draw_face(cube[3])
    draw_face(cube[4])
    draw_face(cube[5])

#start
stdscr = curses.initscr()
# Keine Anzeige gedrückter Tasten
curses.noecho()
# Kein line-buffer
curses.cbreak()
# Escape-Sequenzen aktivieren
stdscr.keypad(1)

# Farben
init_colors()

state = [[0,1,2,3,4,5,6,7],[0,0,0,0,0,0,0,0],[0,1,2,3,4,5,6,7,8,9,10,11],[0,0,0,0,0,0,0,0,0,0,0,0]]

stdscr.refresh()
draw_cube(state)
# Warten auf Tastendruck
c = stdscr.getch()

# Ende
curses.nocbreak()
stdscr.keypad(0)
curses.echo()
curses.endwin()
