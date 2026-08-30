# 08 — What a surname reveals about caste in Karnataka

Karnataka is absent from the census extract the rest of this repo runs on.
outkast covers nineteen states and Karnataka is not among them, and in the south
it holds only Kerala and Tamil Nadu, so these Public Service Commission select
lists are the only caste-linked name data available for the state.

**Scope, before the numbers.** The candidates applied for and obtained state
government jobs, so nothing here describes Karnataka's population, and the
category is one the candidate declared to claim a quota.

**Recovering the surname.** The last token is a single letter 34% of the time,
and the six commonest are `S`, `R`, `K`, `N`, `B`, `C`. Dropping single letters
gives `Kumar`, `Patil`, `Naik`, `Manjunatha`: two inventories of "Karnataka's
commonest surnames" from one set of 48,395 names. Analysis 04 found Maharashtra
failing the same assumption by writing the surname first.

**Finding.** The guess is wrong about **62 of every 100 Scheduled Caste
candidates and 17 of every 100 General ones**, an error 3.6 times larger for the
group the quota exists for. Analysis 05 found that direction nationally on SECC
and the electoral rolls; this is a different state, source and label set,
pointing the same way. Overall the surname closes 24% of the gap, 52.5 mistakes
per 100 down to 40.0.

Run with `make a08`. Read [the note](note.md).
