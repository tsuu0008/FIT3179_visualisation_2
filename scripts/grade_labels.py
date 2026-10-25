"""Preserve each published W_GRADE code as a separate display category.

No public AWTGS grade or difficulty is inferred from a source code.
"""
GRADES = [f'C{i}' for i in range(1, 7)] + ['3', 'Unknown']
GRADE_COLOURS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#252525', '#6f52a3', '#985d3f', '#9daca9']


def grade_label(value):
    return 'Unknown' if value in [None, '', 'Unknown'] else str(value)
