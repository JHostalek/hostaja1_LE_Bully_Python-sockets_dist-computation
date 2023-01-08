import argparse

from Node import Node

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--real_audio', required=False, type=bool, default=False, help='Use real audio')
    parser.add_argument('--tasks', required=False, help='How many tasks to generate', type=int, default=20)
    parser.add_argument('--data_center_ip', required=False, help='IP of the data center', type=str, default='192.168.56.115')
    parser.add_argument('--message_delay', required=False, help='Delay between all messages', type=float, default=1)
    parser.add_argument('--hold_each_message', required=False, help='Hold on to each message until key is pressed. Cancel by CTRL+E', type=bool, default=False)
    parser.add_argument('--bully_timeout', required=False,
                        help='Time limit for the bully algorithm. Node claims to be the coordinator (leader) if neighbors with higher id do not respond until this timeout expires.',
                        type=float,
                        default=20)
    parser.add_argument('--manual_ip', required=False, help='Manually set the IP of this node', type=str, default=None)
    args = parser.parse_args()

    node = Node(
        data_center_ip=args.data_center_ip,
        real_audio=args.real_audio,
        tasks=args.tasks,
        message_delay=args.message_delay,
        hold_each_message=args.hold_each_message,
        bully_timeout=args.bully_timeout,
        manual_ip=args.manual_ip
    )
