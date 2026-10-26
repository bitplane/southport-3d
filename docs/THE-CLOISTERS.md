# The Cloisters, Corporation Street

The researched former Christ Church Higher Grade School replaces only the school portion of the old `chapel-boots-range` placeholder. The marked snag did not identify the selected Town Hall asset. Projecting the saved box through its camera located the school side of that merged retail bound; actual Maps 3D and property photographs established the detached building.

The source represents the 2025 exterior: red brick and sandstone, four frontage bays with eight tall stained-glass lights, two central gabled parapets, octagonal pinnacles, the left pointed entrance with Techedia lettering and three shuttered retail apertures. Porches, reveals and major profiles have geometry; small leadwork and relief are reduced at Walk and baked at District. The foliage is a restrained interpretation of the visible carving, not a scan. No unseen inscription or interior is reconstructed.

Actual Google 3D views were loaded from four quadrants. They show two parallel main slate roofs, a long rear-slope rooflight, lower rear roof/recess and short higher corner roof. The street frontage does not continue all the way to Chapel Street: Boots and the other retail ranges are separate. The old combined placeholder has been cut back to expose the service separation. The court asset owns the new ground; its existing heights are retained.

Private imagery: May 2011 loaded Street View at Corporation Street; 2025 Fitton Estates exterior and stained-glass photographs; Google aerial scale bar and four 3D quadrants, accessed 26 October 2026. Source URLs, raw image landmark inputs and confidence are in `research/`. Street View requests behind the school snapped to the front panorama; rear ground-level detail is unavailable. Mapillary web search yielded no useful coverage. A similarly named Historic England school in Crosby was rejected as the wrong building. All photographic pixels remain outside Git and exported assets.

The footprint is an estimated 16.3 × 18.3 m. Roof scale-bar ratios and the advertised 270.76 m² lower-floor internal area provide a cross-check; global placement retains the agreed church court edge. Eaves 11.4 m, main ridge 14.35 m and gabled parapets 15 m are estimated above the existing 0.7845 m entrance datum. Plan uncertainty is about 1.2 m and height uncertainty about 1 m. The nearby station rough grid is a different support owner and was not substituted for the court's established threshold.

Before detail, front/corner and overhead massing renders were compared with the actual 3D west/north orbits: roof ordering, lower rear shape and detached outline agreed at block scale. The later detailed render review corrected the pointed arches, sandstone tone, backwards lettering and pinnacle caps; inner pinnacle tops were lowered below the gable peaks after checking their relative silhouette. Fine rear windows, exact rear equipment, full foliage and inscriptions remain incomplete; modelled court openings retain medium-confidence interpretation.

District is a separately authored bounded envelope: three shared atlases 512², 512 × 256 and 256², total caps 900 triangles / 2 MB download / 8.5 MB estimated GPU memory. The tighter export regression caps the resulting school at 500 triangles. Five pinnacle envelopes, twin parapets, paired roofs and rear step retain silhouette independently of added ornament. Small glazing bars, drainage and individual carved motifs are omitted from coarse geometry. Receiver cages are 0.9 m at the projecting porch and 0.65 m elsewhere, with 0.5 m pinnacle cages. The atlas floor is about 7.34 MB before meshes.


A supplementary [January 2023 restoration photograph](https://standupforsouthport.com/techedia-transforms-historic-southport-landmark-into-stunning-new-offices-with-1m-investment/) confirms the entrance sign, black panelled doors, sandstone carving and shop transom arrangement. Targeted searches for a dimensioned floor plan/planning drawing did not produce one; the dimensions remain estimates. The 2025 brochure's area is for Unit 1, not a surveyed footprint of the entire school.

Final source renders reviewed: front, corner, church side, rear and overhead. Front and corner were compared with Fitton's full elevation and May 2011 Street View; roof and rear with Google 3D headings 0/90/180/270. Fine foliate carving, precise corporate logo geometry, unobserved rear details and detailed roof equipment remain simplified. The main master has 42,288 triangles; all-shell/all-trim coplanarity, float32 geometry and the existing entrance datum check passed. Initial exported Detail/Walk scans found only four self-contact residues in `Architecture court pilaster`, each 0.00000118–0.00000230 m², below the declared 0.000005 m² regression threshold; these are float32 clipping-edge residues, not accepted duplicate wall areas.

The available 3D imagery does not give a reliable capture date. Its roof layout is retained as the observed shape; the 2023 report described a future roof-terrace fit-out, so later terrace furniture/railings are not asserted or invented.


Final published package costs:

| Level | Triangles | Download bytes | Estimated GPU bytes |
| --- | ---: | ---: | ---: |
| Detail | 42,288 | 5,989,948 | 10,308,915 |
| Walk | 25,907 | 3,753,636 | 8,134,931 |
| District | 140 | 452,460 | 7,355,092 |

The project build, source validation, all three exported-level checks and package checks passed with four Blender threads. The assembled published neighbour audit included Christ Church, its approach, Town Hall, station placeholders and station ground. It found no cross-asset overlap involving the school at any level. Detail and Walk each retain only the four documented tiny self-contact residues (combined 0.000006465 m²); District has none. Existing findings elsewhere in that neighbourhood are outside this change.

Actual local viewer review on 26 October 2026 confirmed the school resource loaded independently in forced Detail, Walk and District, with no failed resources. Front/corner comparison, a close entrance view and overhead roof review verified the paired roof silhouette, gables, lower rear roof and separation from the adjacent retail placeholder. In walking mode the new side gap settled at eye height 2.484500 m, matching the retained 0.7845 m court plus the viewer's 1.7 m eye height. Exported access rays also remain clear at every level. Automatic selection chose Walk at 25.66 m and District at 121.60 m. Private screenshots and audit reports are retained in ../output/cloisters/; they are not publication inputs or tracked reference imagery.
