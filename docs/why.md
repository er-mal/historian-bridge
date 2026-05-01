# Why HistorianBridge

> The longer pitch. The README has the 30-second version.

## The problem you actually have

Every plant data project re-writes the same vendor glue, and that work
disappears the next time the historian changes. That glue is a tax on
every analytics initiative — Grafana dashboards, OEE calculations,
predictive-maintenance pilots, ESG reporting, anything that needs
sensor history.

The tax shows up as:

- **Lock-in** — the vendor owns the API surface your analytics team
  depends on. Migration cost grows with every dashboard built.
- **Re-work** — every consumer (Grafana plugin, Python notebook, MES
  query) is written against the vendor's wire format. Swap the vendor
  and you re-write all of them.
- **OT/IT friction** — every new consumer is a new connection your OT
  team has to security-review against the historian.

## What HistorianBridge is

A **stable contract** between the historian and everything downstream.
One typed HTTP API. Drivers swap underneath without consumers knowing.

It's the same architectural move as putting a load balancer in front of
backends, or an ORM in front of databases. Boring. Well-understood.
The novelty is that nobody bothered to do it for industrial historians
because each vendor benefits from you not doing it.

## What it gets you

- **Vendor independence.** Migrate from PI to Influx (or back, or run
  both during cutover) without rewriting consumers.
- **One audit surface.** OT reviews HistorianBridge once. New
  consumers go through it instead of getting their own historian
  credentials.
- **Apache-2.0.** Fork it, embed it, vendor it into your platform. No
  SaaS. No phone-home. No per-tag pricing.
- **Honest scope.** Read-only. Two backends. Non-goals are written
  down ([validation.md §5](validation.md)). We ship what we ship.

## What it is not

- Not a historian. It does not store anything.
- Not a write path. v1 cannot mutate the historian.
- Not a multi-tenant cloud. It runs as a local binary or sidecar.
- Not a migration tool. It lets you migrate, but does not move data.

## The pitch in one sentence

Stop letting your historian vendor own the API surface that your
analytics team depends on.
