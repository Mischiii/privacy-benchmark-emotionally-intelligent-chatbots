import argparse

BOT_MAP = {
    "Character.ai": "character_ai",
    "Replika": "replika",
    "Nomi.ai": "nomi_ai",
    "Kindroid": "kindroid"
}

CHARACTER_MAP = {
    "Emilia": "emilia",
    "Matteo": "matteo",
    "Ms.Smith": "ms_smith",
    "Satoru": "satoru_gojo"
}

ENHANCEMENT_MAP = {
    "Chain-of-Thought-Reasoning": "cot",
    "Self-Defense": "self-defense",
    "Self-Defense-Proxy": "self-defense-proxy"
}

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def transform_args(args):
    args.benchmark_bot = BOT_MAP.get(args.benchmark_bot, args.benchmark_bot)
    if hasattr(args, 'benchmark_character') and args.benchmark_character:
        args.benchmark_character = CHARACTER_MAP.get(args.benchmark_character, args.benchmark_character)
    if hasattr(args, 'enhancement_method') and args.enhancement_method:
        args.enhancement_method = ENHANCEMENT_MAP.get(args.enhancement_method, args.enhancement_method)
    return args

def add_common_arguments(parser):
    parser.add_argument(
        "--benchmark-bot",
        required=True,
        choices=list(BOT_MAP.keys()),
        help="Select the benchmark bot."
    )

    parser.add_argument(
        "--benchmark-character",
        required=True,
        choices=list(CHARACTER_MAP.keys()),
        help="Name of the benchmark character."
    )

    parser.add_argument(
        "--enhancement-method-enabled",
        type=str2bool,
        required=True,
        help="Enable enhancement method (True/False)."
    )

    parser.add_argument(
        "--enhancement-method",
        choices=list(ENHANCEMENT_MAP.keys()),
        help="Enhancement method to use (optional)."
    )

def add_keyword_arguments(parser):
    parser.add_argument(
        "--benchmark-bot",
        required=True,
        choices=list(BOT_MAP.keys()),
        help="Select the benchmark bot."
    )
    parser.add_argument(
        "--benchmark-character",
        required=False,
        choices=list(CHARACTER_MAP.keys()),
        help="Name of the benchmark character."
    )
    parser.add_argument(
        "--enhancement-method-enabled",
        type=str2bool,
        required=False,
        help="Enable enhancement method (True/False)."
    )
    parser.add_argument(
        "--enhancement-method",
        choices=list(ENHANCEMENT_MAP.keys()),
        required=False,
        help="Enhancement method to use (optional)."
    )
    parser.add_argument(
        "--task",
        choices=["extract-character-keywords", "summarize-chatbot-keywords"],
        required=True,
        help="Performed Task (extract-character-keywords, summarize-chatbot-keywords.)"
    )

def validate_enhancement_args(args, parser):
    if args.enhancement_method_enabled and not args.enhancement_method:
        parser.error("--enhancement-method must be set if --enhancement-method-enabled is True.")
    if not args.enhancement_method_enabled and args.enhancement_method:
        parser.error("--enhancement-method should not be set if --enhancement-method-enabled is False.")

def perform_benchmark_argparsing():
    """
    Performs argument parsing and provides the user with instructions on how to use the framework.

    :return (argparse.Namespace): Parsed Arguments.
    """
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)

    parser.add_argument(
        "--benchmark-tier",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help="Benchmark tier (1, 2, or 3)."
    )

    parser.add_argument(
        "--benchmark-variant",
        type=int,
        choices=[1, 2, 3],
        required=True,
        help="Benchmark variant (1, 2, or 3)."
    )

    args = parser.parse_args()
    validate_enhancement_args(args, parser)
    return transform_args(args)

def perform_evaluation_argparsing():
    """
    Performs argument parsing and provides the user with instructions on how to use the framework.

    :return (argparse.Namespace): Parsed Arguments.
    """
    parser = argparse.ArgumentParser()
    add_common_arguments(parser)
    args = parser.parse_args()
    validate_enhancement_args(args, parser)
    return transform_args(args)

def perform_keyword_extraction():
    """
    Performs argument parsing and provides the user with instructions on how to use the framework.

    :return (argparse.Namespace): Parsed Arguments.
    """
    parser = argparse.ArgumentParser()
    add_keyword_arguments(parser)
    args = parser.parse_args()
    return transform_args(args)