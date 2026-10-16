# Scala/Spark RDD analysis

This is the final RDD execution path. It reads one canonical catalog
CSV from the repository's `data\review3_catalog.csv`,
and does not read the original D: dataset or a second input dataset.

The analysis parses the catalog, filters an altitude range, counts categories
with a key-value RDD, extracts distinct name/designator tokens, and reduces
altitude. It prints partition counts, actual `toDebugString` lineage, a DAG
explanation, and persistence level. Fault tolerance is explained from the
lineage; this command does not claim that executor failure recovery was
experimentally induced.

## PowerShell execution

```powershell
$base = (Get-Location).Path
$module = Join-Path $base 'phase-2b\spark-rdd'
$catalog = Join-Path $base 'data\review3_catalog.csv'
$m2 = Join-Path $env:TEMP 'space-debris-m2'
$env:PATH = "$jdk\bin;$env:PATH"
$env:MAVEN_OPTS = '--add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/java.nio=ALL-UNNAMED --add-opens=java.base/java.lang.invoke=ALL-UNNAMED --add-opens=java.base/java.util=ALL-UNNAMED'

mvn -f "$module\pom.xml" "-Dmaven.repo.local=$m2" test
mvn -f "$module\pom.xml" "-Dmaven.repo.local=$m2" compile exec:java `
  "-Dexec.args=$catalog 4" `
  '-Dexec.cleanupDaemonThreads=false'
```

The first command verifies parser tests. The second is the executable analysis
run. Save its genuine console output under the repository's
`submission\evidence` directory if a new capture is required.

## Where each required item appears

- RDD creation: `sc.textFile(...).repartition(...)` in `RddAnalysis.scala`.
- Transformations: `map`, `flatMap`, `filter`, `persist`, `reduceByKey`,
  `sortByKey`, `distinct`, and `sortBy`.
- Actions: `count`, `collect`, `take`, and `reduce`.
- Key-value operation: `(record.category, 1)` followed by `reduceByKey`.
- Partitions: `raw_partitions` and `valid_partitions` in the output.
- Lineage/DAG: `lineage` and `dag` output lines.
- Cache/persist: `storage_level` plus repeated actions on the persisted RDD.
- Fault tolerance: the output records lineage-based recomputation; it does not
  claim a machine or executor failure test.

The canonical source schema is the existing joined catalog schema. The RDD job
uses NORAD ID, object type, altitude, orbital period, object name, and
international designator; all other columns remain available in the source
for the separate pipeline and dashboard.
