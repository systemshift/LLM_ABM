"""
CLI entry point: python -m llm_abm "simulate wolves and rabbits"
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="llm_abm",
        description="Generate and run agent-based simulations from natural language",
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="Natural language description of the simulation",
    )
    parser.add_argument(
        "--model", default="gpt-5",
        help="OpenAI model to use (default: gpt-5)",
    )
    parser.add_argument(
        "--steps", type=int, default=None,
        help="Number of simulation steps (default: LLM decides)",
    )
    parser.add_argument(
        "--output", "-o", default=None,
        help="Output file for results (JSON)",
    )
    parser.add_argument(
        "--spec-only", action="store_true",
        help="Only generate the spec, don't run the simulation",
    )
    parser.add_argument(
        "--from-spec", default=None,
        help="Run simulation from an existing spec JSON file",
    )
    parser.add_argument(
        "--api-key", default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--base-url", default=None,
        help="API base URL for compatible endpoints",
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Start an interactive chat session",
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        _interactive(args)
        return

    # Run from existing spec file
    if args.from_spec:
        _run_from_spec(args)
        return

    # Need a prompt for generation
    if not args.prompt:
        parser.print_help()
        sys.exit(1)

    from .chat import generate, run_chat

    if args.spec_only:
        spec = generate(
            args.prompt,
            model=args.model,
            api_key=args.api_key,
            base_url=args.base_url,
        )
        output = json.dumps(spec, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Spec saved to {args.output}")
        else:
            print(output)
        return

    results = run_chat(
        args.prompt,
        steps=args.steps,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
    )

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {args.output}")
    else:
        summary = results.get("summary", {})
        print(json.dumps(summary, indent=2))


def _run_from_spec(args):
    """Run simulation from a spec file."""
    from .core.simulation import Simulation

    with open(args.from_spec) as f:
        spec = json.load(f)

    steps = args.steps or spec.pop("steps", 200)
    sim = Simulation(spec)

    print(f"Running {steps} steps from {args.from_spec}...")
    results = sim.run(steps)

    summary = results.get("summary", {})
    print(f"Done. Final population: {summary.get('final_counts', {})}")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(summary, indent=2))


def _interactive(args):
    """Interactive chat session."""
    from .chat import ChatSession

    print("LLM-ABM Interactive Session")
    print(f"Model: {args.model}")
    print("Type a simulation description, or 'quit' to exit.\n")

    session = ChatSession(
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
    )

    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Bye!")
            break

        try:
            results = session.send(user_input, steps=args.steps)
            summary = results.get("summary", {})
            print(f"\nResults: {json.dumps(summary, indent=2)}\n")

            if args.output:
                with open(args.output, "w") as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"Saved to {args.output}\n")

        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
