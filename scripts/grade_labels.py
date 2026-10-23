"""Plain-language display labels; raw walking-grade values remain unchanged.

This is a documented label normalisation, not a new AWTGS assessment. C6 has
no public Grade 6 counterpart and stays Unclassified rather than being reassigned.
"""
GRADES = [f'Grade {i}' for i in range(1, 6)] + ['Unclassified', 'Unknown']
GRADE_COLOURS = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#252525', '#6f52a3', '#9daca9']


def grade_label(value):
    if value in [None, '', 'Unknown']:
        return 'Unknown'
    if value == 'C6':
        return 'Unclassified'
    return {**{f'C{i}': f'Grade {i}' for i in range(1, 6)}, '3': 'Grade 3'}[value]
