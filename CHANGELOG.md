# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Analysis 09, whether the village premium travels outside Bihar.** Analysis
  02 is the strongest result here and it rested on one state. Scored on the same
  protocol in Gajapati district, Odisha, a village adds 20 points where in Bihar
  it adds 30; against what the surname leaves unresolved, it closes 42% of the
  remainder against Bihar's 64%. Three analyst's choices were varied and none
  produces the result: the jati merge threshold moves it by half a mistake,
  stripping the religion suffix from the label moves it from 19.7 to 15.8, and
  changing which token is taken as the surname moves it by 0.2. The surname
  position is measured from the father's name rather than assumed, and in
  Gajapati the surname is last, the opposite of Maharashtra.

- **Analysis 07, where a surname works and where it does not.** The national
  figure hides a spread from 67% of the gap closed in Assam to 0% in Haryana.
  What carries a state is one or two large decisive names, not many of them:
  Punjab has five majority-Dalit surnames among its 25 commonest and closes 3%,
  Assam has two and closes 67%, because one of them is `das`. Each state's
  coverage is printed beside its result, and the ordering survives cutting every
  state to its 25 commonest names.
- **Analysis 08, Karnataka.** 34% of last tokens there are a single letter, and
  the ten commonest all are. Cleaning them changes the surname inventory
  completely and the prediction not at all, 49.2 against 49.6 per 100 with a
  blind rate of 54.5 -- slightly worse, because smaller cells resolve fewer
  people. Reported as the null it is.

- The front page now shows the skew. Sorted by frequency, the ten commonest
  surnames in India cover 32% of everybody and not one of them moves the guess
  off the base rate, while the 2,930 names ranked 1001 and below cover 6% of
  people and 625 of them do. The figure pairing frequency against Dalit share
  was already built and was not linked from the README.

## [1.0.1] - 2026-08-26

One wrong sentence in the most citable claim, and the reversal it forces.

### Fixed

- **A wrong sentence in the most citable claim.** The front page and analysis 05
  said "a Dalit is guessed wrong 29 times in 100 against a blind rate of 30 --
  the name buys essentially nothing". The 29 was `1 - max(p)` averaged over the
  Dalits carrying each name, which measures how vague those names are; it is a
  property of names, not of people, and it was set against a population-wide
  blind rate. Scored consistently, the guess is wrong about 66 of every 100
  Dalits and 4 of every 100 people outside the schedules, and those weight up to
  the 20-per-hundred headline exactly.

  This reverses part of the old claim. The name is not useless for Dalits: it
  takes them from wrong about all of them to wrong about 66 in a hundred, and it
  does more still for Adivasis. What survives, and is stronger, is the disparity --
  seventeen-fold -- and the consequence for audits, which now rests on the right
  mechanism: two thirds of Dalits land in the comparison group.

  `by_caste` now reports `wrong_per_100`, `blind_wrong_per_100` and the old
  quantity renamed `name_vagueness_per_100`, and the figure plots recall error
  against each group's own blind rate rather than plotting vagueness under an
  axis labelled as error.
- Coverage for the sex split is now measured after the merge onto the caste
  table in analysis 05's own note, matching the front page.

## [1.0.0] - 2026-08-26

Six analyses of one question: pick a person at random, know only their last
name, and how often are you wrong about their caste?

The answer is a bracket rather than a number. Knowing nothing costs 25 mistakes
per hundred and the name alone costs 20, so the name is worth about five. Put
the same name next to a village and it is worth thirty. That gap, not the
average, is the finding.

### Analyses

- **01 surname to category.** All-India SC/ST/Other from SECC. The name saves
  five mistakes per hundred on average, changes nothing for 91% of people, and
  the three commonest surnames in India are among the least informative.
- **02 surname by geography.** Bihar land records, 141 jatis. A surname and a
  village leave 17 mistakes per hundred; the surname alone leaves 47.
- **03 how few names.** India's commonest last name records the bearer's sex,
  not her family. Names of that kind cover 10.5% of the country and make Indian
  naming look far more concentrated than it is.
- **04 which token is the surname.** A token shared between an elector and their
  father or husband is an inherited one. The test confirms ten sex-marking names,
  splits Singh (78% transmitted) from Kumar (8%), and found that Maharashtra
  writes the surname first, which withdrew two states from analysis 03.
- **05 who has an uninformative name.** The errors are not spread evenly. A
  Dalit is guessed wrong 29 times per hundred against a blind rate of 30; someone
  outside the schedules, 17. The method is accurate about the advantaged and
  blind about the disadvantaged. *(Corrected in Unreleased: the 29 was not what
  this sentence claims it was.)*
- **06 neighbours.** Holding out whole villages, the surrounding surnames rescue
  precisely the names that say nothing alone. Chaudhary goes from 80 mistakes to
  56. The bracket closes at 9 once the roll's cues are matched against a caste
  register.

### Added

- `tests/test_readme_numbers.py` pins all 28 headline figures on the front page
  to the outputs they come from, so a re-run analysis cannot silently leave a
  stale number in the README.
- `src/last_name_basis/upnaam.py`, a validated reader for versioned
  recorded-surname resolution.

### Fixed

- The front page claimed an electoral roll gets you to 9 mistakes per hundred.
  Caste is printed on no roll; the 9 requires matching the roll's cues against a
  caste register of the same population.
- All four rows of analysis 06's bracket are now scored on the same held-out
  villages. They had been split independently and shared only 2,509 of some
  8,300 test villages, so the rows described different people.
- The front page quoted two different blind rates, 25 and 30, without saying
  that the first is weighted by the electoral roll and the second by SECC.
- Analysis 02's surname-and-village figure was the plug-in estimate, 16. Half
  those cells hold one household, so the leave-one-out figure of 17 is the one
  that answers the question.
- The share of people whose name makes the guess *harder* was given as 32%,
  which matched neither weighting. It is 16%.
- Sex-marking names were said to cover 19% of the country. That figure includes
  Singh and Kumar, which analysis 04 shows are not the same case. The
  sex-marking names alone cover 10.5%.
- `in-rolls/jati` is private, and analyses 02 and 06 read their ladders from a
  local clone of it. The README linked it as though a reader could follow.

[Unreleased]: https://github.com/in-rolls/last-name-basis/compare/v1.0.1...HEAD
[1.0.1]: https://github.com/in-rolls/last-name-basis/releases/tag/v1.0.1
[1.0.0]: https://github.com/in-rolls/last-name-basis/releases/tag/v1.0.0
