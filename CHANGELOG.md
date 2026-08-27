# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

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
  blind about the disadvantaged.
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

[Unreleased]: https://github.com/in-rolls/last-name-basis/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/in-rolls/last-name-basis/releases/tag/v1.0.0
