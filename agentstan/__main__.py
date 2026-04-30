"""
CLI entry point: python -m agentstan "simulate wolves and rabbits"
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="agentstan",
        description="AgentStan: AI-native agent-based modeling. Simulate, Test, Analyze, Narrate.",
    )
    parser.add_argument("prompt", nargs="?", help="Natural language simulation description")
    parser.add_argument("--model", default="gpt-5.5", help="OpenAI model (default: gpt-5.5)")
    parser.add_argument("--steps", type=int, default=200, help="Simulation steps (default: 200)")
    parser.add_argument("--output", "-o", default=None, help="Output file (JSON)")
    parser.add_argument("--from-spec", default=None, help="Run from existing spec JSON file")
    parser.add_argument("--batch", type=int, default=None, help="Run N times (batch mode)")
    parser.add_argument("--analyze", action="store_true", help="Run population analysis on results")

    args = parser.parse_args()

    if args.from_spec:
        _run_from_spec(args)
    elif args.prompt:
        _run_from_prompt(args)
    else:
        parser.print_help()
        sys.exit(1)


def _run_from_spec(args):
    from .core.simulation import Simulation

    with open(args.from_spec) as f:
        spec = json.load(f)

    steps = args.steps or spec.pop("steps", 200)

    if args.batch:
        from .experiment import batch_run
        print(f"Batch running {args.batch} times, {steps} steps each...")
        results_list = batch_run(spec, n_runs=args.batch, steps=steps)
        _output_batch(results_list, args)
    else:
        sim = Simulation(spec)
        print(f"Running {steps} steps...")
        results = sim.run(steps)
        _output_single(results, args)


def _run_from_prompt(args):
    from .ai.generate import generate

    print(f"Generating simulation from: \"{args.prompt}\"")
    spec = generate(args.prompt, model=args.model)

    name = spec.get("metadata", {}).get("name", "Simulation")
    agent_types = list(spec.get("agent_types", {}).keys())
    print(f"Created: {name} ({', '.join(agent_types)})")

    if args.batch:
        from .experiment import batch_run
        print(f"Batch running {args.batch} times, {args.steps} steps each...")
        results_list = batch_run(spec, n_runs=args.batch, steps=args.steps)
        _output_batch(results_list, args)
    else:
        from .core.simulation import Simulation
        sim = Simulation(spec)
        print(f"Running {args.steps} steps...")
        results = sim.run(args.steps)
        _output_single(results, args)


def _output_single(results, args):
    summary = results.get("summary", {})
    print(f"Final: {summary.get('final_counts', {})}")

    if args.analyze:
        from .analysis.population import analyze
        report = analyze(results)
        for agent_type, info in report.get("agent_types", {}).items():
            print(f"  {agent_type}: {info.get('stability', '?')}", end="")
            if info.get("period"):
                print(f" (period ~{info['period']})", end="")
            if info.get("extinct"):
                print(f" EXTINCT at step {info['extinction_step']}", end="")
            print()

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"Saved to {args.output}")


def _output_batch(results_list, args):
    # Aggregate summaries
    from collections import Counter
    all_types = set()
    for r in results_list:
        all_types.update(r["summary"]["final_counts"].keys())

    for t in sorted(all_types):
        finals = [r["summary"]["final_counts"].get(t, 0) for r in results_list]
        avg = sum(finals) / len(finals)
        extinct = sum(1 for f in finals if f == 0)
        print(f"  {t}: avg={avg:.1f}, extinct in {extinct}/{len(finals)} runs")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(results_list, f, indent=2, default=str)
        print(f"Saved {len(results_list)} results to {args.output}")


if __name__ == "__main__":
    main()
