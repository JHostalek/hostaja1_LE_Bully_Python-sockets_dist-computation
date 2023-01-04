from Node import Node


if __name__ == '__main__':
    node = Node()
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
        exit(0)
