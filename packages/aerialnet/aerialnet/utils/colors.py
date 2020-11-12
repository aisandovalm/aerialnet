import warnings


def label_color(label):
    """ Return a color from a set of predefined colors. Contains 80 colors in total.

    Args
        label: The label to get the color for.

    Returns
        A list of three values representing a RGB color.

        If no color is defined for a certain label, the color green is returned and a warning is printed.
    """
    if label < len(colors):
        return colors[label]
    else:
        warnings.warn('Label {} has no color, returning default.'.format(label))
        return (0, 255, 0)


"""
Generated using:

```
colors = [list((matplotlib.colors.hsv_to_rgb([x, 1.0, 1.0]) * 255).astype(int)) for x in np.arange(0, 1, 1.0 / 80)]
shuffle(colors)
pprint(colors)
```
"""
colors = [
    (80,80,80),
    (200,90,90),
    (00,200,90),
    (60,90,200),
    (20,90,150),
    (0,180,0),
    (0,180,200),
    (0,0,255),
    (50,50,255), 
    (30,200,20), 
    (250,0,255), 
    (0,0,0),
    (80,80,80),
    (200,90,90),
    (00,200,90),
    (60,90,200),
    (20,90,150),
    (0,180,0),
    (0,180,200),
    (0,0,255),
    (50,50,255), 
    (30,200,20), 
    (250,0,255), 
    (0,0,0),
    (80,80,80),
    (200,90,90),
    (00,200,90),
    (60,90,200),
    (20,90,150),
    (0,180,0),
    (0,180,200),
    (0,0,255),
    (50,50,255), 
    (30,200,20), 
    (250,0,255), 
    (0,0,0)
]