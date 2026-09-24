# Geographical Drill — Global Map + Country Matrix Architecture

## Status

Design requirement for the 0.3 central-motor line.

## Purpose

CareerHub must let a user choose **any location in the world** while still taking advantage of authoritative national and subnational geography where structured country matrices are available.

The geographical drill therefore has two cooperating layers:

1. **Global selection and travel layer — Google Maps Platform**
2. **Country-matrix enrichment layer — authoritative national/regional datasets**

Neither layer replaces the other.

## 1. Global selection layer

Google Maps Platform provides the universal location interface.

Supported user entry modes should include:

- search/autocomplete for a place or address,
- clicking or dropping a pin on the map,
- choosing an arbitrary latitude/longitude,
- selecting a city/locality/administrative area/country,
- radius around a selected point,
- travel-time or route-distance expansion,
- remote/global search independent of physical geography.

The normalized global anchor must retain, when available:

- Google Place ID,
- latitude/longitude,
- formatted display name,
- country / ISO country code,
- locality,
- administrative-area components,
- postal-area components where relevant,
- user-selected radius or travel-time constraints.

Google Maps data is the interaction and routing substrate. It is not the authoritative national statistical matrix.

## 2. Country matrix layer

Once the selected anchor resolves to a country, CareerHub checks a country-adapter registry.

If a supported country adapter exists, the anchor is enriched with the country's official geography and functional-labour-market structures.

Conceptual flow:

```text
GOOGLE MAP / PLACE / PIN
        |
        v
GLOBAL GEO ANCHOR
place_id + lat/lng + ISO country
        |
        +-----------------------------+
        |                             |
        v                             v
COUNTRY ADAPTER EXISTS          NO COUNTRY ADAPTER
        |                             |
        v                             v
OFFICIAL COUNTRY MATRIX         GOOGLE-ONLY GEO MODEL
        |
        v
ADMINISTRATIVE + FUNCTIONAL DRILL
```

## 3. Sweden adapter — first implementation

Country code: `SE`

Authoritative hierarchy:

```text
Sweden
  -> Län
      -> Kommun
          -> RegSO
              -> DeSO
```

Functional overlays:

- Local Labour Market (LA),
- FA region where available,
- metropolitan-area classification,
- SKR municipality classification where used,
- municipality adjacency / relational graph,
- commuting and travel-time relations where available.

For CareerHub, functional labour-market relationships should normally have greater search value than physical border adjacency alone.

## 4. Drill modes

The geographical drill should support several independent modes.

### A. Administrative drill

Country -> first-order region -> municipality/local authority -> statistical subarea.

### B. Functional labour-market drill

Selected place -> local labour market -> linked municipalities -> neighbouring/related labour markets.

### C. Radius drill

Selected map point -> N km radius.

### D. Travel-time drill

Selected origin -> destinations reachable within a configured travel-time threshold.

Travel-time may use routing data rather than straight-line distance.

### E. Progressive widening

Example:

```text
exact selected place
  -> municipality/locality
  -> functional labour market
  -> adjacent/commuting municipalities
  -> region/county
  -> neighbouring functional regions
  -> country
  -> remote / international
```

The widening sequence must be configurable by profile and by search session.

### F. Manual world selection

The user may bypass all national drill logic and select any location or set of locations directly on the global map.

## 5. Country adapter registry

CareerHubZero should expose a registry such as:

```yaml
countries:
  SE:
    adapter: scb
    status: supported
    administrative_matrix: true
    functional_labour_market: true
    fine_statistical_areas: true

  XX:
    adapter: null
    status: google_only
```

The global engine must never require a country adapter to function.

Adding another country is therefore a data/adapter expansion, not a redesign of the CareerHub geography engine.

## 6. Canonical geo object

A search session should normalize geography into a provider-independent object.

Illustrative shape:

```yaml
geo_anchor:
  source: google_maps
  place_id: "..."
  coordinates:
    lat: 0.0
    lng: 0.0
  country_code: SE
  locality: "Uppsala"
  administrative_components: {}
  country_matrix:
    adapter: scb
    county_code: null
    municipality_code: null
    regso_code: null
    deso_code: null
    labour_market_code: null
  drill:
    mode: progressive
    radius_km: null
    travel_time_minutes: null
    transport_mode: null
```

Google-specific identifiers must not become the only internal key. Country-matrix IDs and CareerHub's own normalized geo identifiers must remain independently addressable.

## 7. Authority and precedence

When layers disagree:

1. official country-matrix identifiers govern the national administrative/statistical classification,
2. Google Maps governs map interaction, place discovery, geocoding/routing context and user-selected coordinates,
3. CareerHub records both without silently rewriting one into the other.

Unknown or unsupported country-level classifications remain unknown.

## 8. CareerHub search integration

Geography is part of the **search raster**, never candidate evidence.

The geographical drill may affect:

- job-source queries,
- ranking,
- widening/narrowing of result sets,
- commute feasibility,
- travel-time filtering,
- remote/hybrid interpretation,
- display/map grouping.

It must not create claims about the candidate.

## 9. 0.3 implementation requirement

Before 0.3 can claim a complete geographical drill:

- global Google Maps/Places selection contract exists,
- provider-independent geo-anchor schema exists,
- country-adapter registry exists,
- Sweden adapter is implemented from authoritative matrices,
- progressive widening logic exists,
- radius and travel-time drill contracts exist,
- geo settings are consumable by sourcing/ranking,
- unsupported countries fall back cleanly to Google-only operation,
- tests prove that the same search engine works with and without a country adapter.


## 10. Job-ad geotagging and zoom clustering

Every sourced vacancy must receive a normalized `geo` object before map rendering.

Resolution order:

1. source-native coordinates, if the vacancy source provides them,
2. explicit workplace/street address from the vacancy,
3. explicit locality/municipality/region string from the vacancy,
4. optional employer + location Google lookup only when explicitly enabled,
5. unresolved/remote state when no defensible spatial anchor exists.

CareerHub must never fabricate street-level precision. A vacancy that only says `Stockholm, Stockholms län` is tagged at **locality precision** and remains grouped at Stockholm. A vacancy that contains a defensible workplace address may become a precise map point.

### Map behaviour

The map is zoom-aware.

```text
WORLD / COUNTRY VIEW
Sweden 412
   ↓ zoom

REGIONAL VIEW
Stockholms län 183
Uppsala län 61
Skåne län 47
   ↓ zoom

CITY VIEW
Stockholm 153
Solna 18
Sundbyberg 7
Uppsala 49
   ↓ zoom

CLOSE CITY VIEW
precise vacancy points spread to their real geotagged positions
+
coarse city-only vacancies remain as a Stockholm locality cluster
```

A cluster exposes both:
- `count`: all represented jobs,
- `new_count`: jobs first discovered in the latest scan.

So a Stockholm hover can show, for example:

```text
Stockholm
153 jobs
18 newly sourced
```

Zooming in does not randomly scatter those 153 jobs. Only ads with sufficiently precise evidence split into individual points. The remainder stay visibly grouped as city-level vacancies.

### Runtime

Central implementation:
- `src/careerhub/geography.py`
- `scripts/geotag_jobs.py`
- `schemas/job_geo.schema.json`

Example:

```bash
GOOGLE_MAPS_API_KEY=... \
python scripts/geotag_jobs.py data/job_vault.json \
  --region-code SE \
  --map-output data/map.json \
  --zoom 8 \
  --latest-only
```

At high zoom the map payload switches to mixed mode:
- precise point features are emitted individually,
- locality-only jobs remain grouped,
- unresolved jobs are not given invented coordinates.

Country-matrix enrichment is a separate step on top of the geotag and will populate `geo.country_matrix`.
