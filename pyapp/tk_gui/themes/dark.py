# create Dark theme based on Equilux (GPLv3)
# https://github.com/TkinterEP/ttkthemes/blob/master/ttkthemes/png/equilux/equilux.tcl  # noqa: E501

from tkinter.ttk import Style


def dark_theme(s: Style):
    # fg = "#a6a6a6"
    fg = "#ffffff"
    bg = "#464646"
    # disabledbg = "#2e2e2e"
    # disabledfg = "#999999"
    disabledfg = "#888888"
    # selectbg = "#414141"
    selectbg = "#000000"
    selectfg = "#a6a6a6"
    # selectfg = "#ffffff"
    window = "#373737"
    focuscolor = "#bebebe"
    # checklight = "#e6e6e6"

    s.configure(
        '.',
        background=bg,
        foreground=fg,
        troughcolor=bg,
        selectbackground=selectbg,
        selectforeground=selectfg,
        fieldbackground=window,
        focuscolor=focuscolor,
    )
    s.map('.', foreground=(('disabled', disabledfg),))

    # s.layout('TButton', [
    #     ('Button.button', {'children': [
    #         ('Button.focus', {'children': [
    #             ('Button.padding', {'children': [
    #                 ('Button.label', {'side': 'left', 'expand': 1}),
    #             ]}),
    #         ]}),
    #     ]}),
    # ])

    # s.layout('Toolbutton', [
    #     ('Toolbutton.button', {'children': [
    #         ('Toolbutton.focus', {'children': [
    #             ('Toolbutton.padding', {'children': [
    #                 ('Toolbutton.label', {'side': 'left', 'expand': 1}),
    #             ]}),
    #         ]}),
    #     ]}),
    # ])

    # s.layout('Vertical.TScrollbar', [
    #     ('Vertical.Scrollbar.trough', {'sticky': 'ns', 'children': [
    #         ('Vertical.Scrollbar.thumb', {'expand': 1}),
    #     ]}),
    # ])

    # s.layout('Horizontal.TScrollbar', [
    #     ('Horizontal.Scrollbar.trough', {'sticky': 'ew', 'children': [
    #         ('Horizontal.Scrollbar.thumb', {'expand': 1}),
    #     ]}),
    # ])

    # s.layout('TMenubutton', [
    #     ('Menubutton.button', {'children': [
    #         ('Menubutton.focus', {'children': [
    #             ('Menubutton.padding', {'children': [
    #                 ('Menubutton.indicator', {'side': 'right'}),
    #                 ('Menubutton.label', {'side': 'right', 'expand': 1}),
    #             ]}),
    #         ]}),
    #     ]}),
    # ])

    # s.layout('TCombobox', [
    #     ('Combobox.field', {'sticky': 'nswe', 'children': [
    #         ('Combobox.downarrow', {
    #             'side': 'right',
    #             'sticky': 'ns',
    #             'children': [
    #                 ('Combobox.arrow', {'side': 'right'}),
    #             ],
    #         }),
    #         ('Combobox.padding', {
    #             'expand': 1,
    #             'sticky': 'nswe',
    #             'children': [
    #                ('Combobox.textarea', {'sticky': 'nswe'}),
    #             ],
    #         }),
    #     ]}),
    # ])

    # s.layout('TSpinbox', [
    #     ('Spinbox.field', {
    #         'side': 'top',
    #         'sticky': 'we',
    #         'children': [
    #             ('Spinbox.buttons', {
    #                 'side': 'right',
    #                 'children': [
    #                     (None, {
    #                         'side': 'right',
    #                         'sticky': (),
    #                         'children': [
    #                             ('Spinbox.uparrow', {
    #                                 'side': 'top',
    #                                 'sticky': 'nse',
    #                                 'children': [
    #                                     ('Spinbox.symuparrow', {
    #                                         'side': 'right',
    #                                         'sticky': 'e'
    #                                     }),
    #                                 ],
    #                             }),
    #                             ('Spinbox.downarrow', {
    #                                 'side': 'bottom',
    #                                 'sticky': 'nse',
    #                                 'children': [
    #                                     ('Spinbox.symdownarrow', {
    #                                         'side': 'right',
    #                                         'sticky': 'e'
    #                                     }),
    #                                 ],
    #                             }),
    #                         ],
    #                     }),
    #                 ],
    #             }),
    #             ('Spinbox.padding', {'sticky': 'nswe', 'children': [
    #                 ('Spinbox.textarea', {'sticky': 'nswe'}),
    #             ]}),
    #         ],
    #     }),
    # ])

    # s.configure('TButton', padding=(8, 4, 8, 4), width=-10, anchor='center')
    # s.configure('TMenubutton', padding=(8, 4, 4, 4))
    # s.configure('Toolbutton', anchor='center')
    # s.configure('TCheckbutton', padding=3)
    # s.map('TRadiobutton', background=(('active', checklight),))
    # s.map('TCheckbutton', background=(('active', checklight),))
    # s.configure('TRadiobutton', padding=3)
    # s.configure('TNotebook', tabmargins=(0, 2, 0, 0))
    # s.configure('TNotebook.Tab', padding=(6, 2, 6, 2), expand=(0, 0, 2))
    # s.map('TNotebook.Tab', expand=(('selected', (1, 2, 4, 2)),))
    s.configure('TSeparator', background=bg)

    s.configure('Treeview', background=window)
    # s.configure('Treeview.Item', padding=(2, 0, 0, 0))
    s.map(
        'Treeview',
        background=(('selected', selectbg),),
        foreground=(('selected', selectfg),),
    )

    # s.map('TCheckbutton',
    #       foreground=[('disabled', 'purple'),
    #                   ('pressed', 'yellow'),
    #                   ('active', 'blue')],
    #       background=[('disabled', 'green'),
    #                   ('pressed', '!focus', 'magenta'),
    #                   ('active', 'orange')],
    #       indicatorcolor=[('selected', 'red'),
    #                       ('pressed', 'cyan')]
    #       )

    s.map('TCheckbutton', indicatorcolor=(('selected', selectbg),))
