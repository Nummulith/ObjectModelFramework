from ObjectModel import ObjectModelItem

def Test(aws):
    print()
    print(aws.CallClasses)

    classes = aws.string_to_classes(aws.CallClasses)

    print(classes)
