import argparse
import re
from collections import defaultdict
from pathlib import Path

from config import Config
from RepositoryCreator import RepositoryCreator


def lua_quote(value) -> str:
    text = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{text}"'


def campaign_owner_by_planet(campaign) -> dict[str, str]:
    owners = {}
    forces = campaign.startingForces
    if forces.empty:
        return owners

    era_forces = forces[forces.Era.astype(str) == str(campaign.eraStart)]
    if era_forces.empty:
        era_forces = forces

    for row in era_forces.itertuples():
        owners.setdefault(str(row.Planet), str(row.Owner).upper())
    return owners


def campaign_adjacency(campaign) -> dict[str, set[str]]:
    adjacent = defaultdict(set)
    planet_names = {planet.name for planet in campaign.planets}
    for planet in planet_names:
        adjacent[planet]

    for route in campaign.tradeRoutes:
        if route.start.name not in planet_names or route.end.name not in planet_names:
            continue
        adjacent[route.start.name].add(route.end.name)
        adjacent[route.end.name].add(route.start.name)

    return adjacent


def campaign_lua_table(campaign) -> str:
    owners = campaign_owner_by_planet(campaign)
    adjacent = campaign_adjacency(campaign)
    lines = ["return {"]

    for planet in sorted(adjacent):
        neighbors = ", ".join(lua_quote(name) for name in sorted(adjacent[planet]))
        lines.append(
            f"    [{lua_quote(planet.upper())}] = "
            f"{{ owner = {lua_quote(owners.get(planet, 'NEUTRAL'))}, "
            f"adjacent = {{{neighbors.upper()}}} }},"
        )

    lines.append("}")
    return "\n".join(lines) + "\n"


def safe_file_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_") or "campaign"


def campaign_export_name(campaign) -> str:
    return campaign.setName if campaign.setName != "Empty" else campaign.name


def export_campaigns(repository, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for campaign in sorted(repository.campaigns, key=lambda c: c.name):
        output_path = output_dir / f"{safe_file_name(campaign_export_name(campaign))}.lua"
        output_path.write_text(campaign_lua_table(campaign), encoding="utf-8")
        print(output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_folder", nargs="?")
    parser.add_argument("-o", "--output", default="campaign_planets_lua")
    args = parser.parse_args()

    config = Config()
    data_folders = [args.data_folder] if args.data_folder else config.dataFolders
    repository = RepositoryCreator().constructRepository(
        data_folders, config.startingForcesLibraryURL
    )
    export_campaigns(repository, Path(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
