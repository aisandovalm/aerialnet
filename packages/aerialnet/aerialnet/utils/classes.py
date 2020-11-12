import warnings


def label_classname(label):
    """ Return a class name from a set of predefined classes names. Contains 7 classes in total.

    Args
        label: The label to get the class for.

    Returns
        A string with the name of the class related to the label.

    """
    if label < len(classes):
        return classes[label]
    else:
        warnings.warn('Label {} has no class name, returning default.'.format(label))
        return 'Other'

def label_classnumber(label):
    """ Return a class name from a set of predefined classes names. Contains 7 classes in total.

    Args
        label: The label to get the class for.

    Returns
        A string with the name of the class related to the label.

    """
    return classes.index(label)

classes = [
    'Animal',
    'Basural-Escombro-MConstrucción',
    'Bus',
    'Camión',
    'Chasis',
    'Cilindro',
    'Estructura',
    'GHorquilla',
    'Juegos',
    'Maquinaria',
    'PalletCaja',
    'Persona',
    'Pickup',
    'Piscina',
    'Poste',
    'SAdvertencia',
    'Tractor',
    'Troncos',
    'Tuberia',
    'Vehículo'
]