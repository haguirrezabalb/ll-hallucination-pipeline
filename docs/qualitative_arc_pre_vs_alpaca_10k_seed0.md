# Qualitative cases - ARC-Easy (seed0) - baseline vs alpaca_10k

- Baseline samples: `evals/baseline/baseline_arc_easy_seed0/__home__USER__models__qwen3-8b-base__Qwen3-8B-Base/samples_arc_easy_2026-01-09T23-57-41.041908.jsonl`

- Post (alpaca_10k) samples: `evals/postqlora/by_adapter/alpaca_10k/arc_easy_seed0/samples_arc_easy_2026-01-10T01-20-34.304423.jsonl`

Selection criterion:

- Correct/incorrect is based on `acc` (unnormalized loglikelihood argmax over choices).
- `acc_norm` is reported for context and may disagree with `acc`.

## Improvements (PRE incorrect → POST correct), top 20

### doc_id=2

Q: Meiosis is a type of cell division in which germ cells divide to produce haploid cells. Where does meiosis occur?

**PRE**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=3 | is_correct=False

- [A] brain cells
- [B] bone cells
- [C] muscle cells  [PRED]
- [D] ovary cells  [GT]

**POST**: acc=1 | acc_norm=0 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] brain cells
- [B] bone cells
- [C] muscle cells
- [D] ovary cells  [PRED ,GT]

### doc_id=3

Q: Which characteristic describes the texture of a kitten's fur?

**PRE**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=3 | is_correct=False

- [A] gray
- [B] warm
- [C] long  [PRED]
- [D] soft  [GT]

**POST**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] gray
- [B] warm
- [C] long
- [D] soft  [PRED ,GT]

### doc_id=11

Q: The circulatory system and the endocrine system work together in the human body. Which describes one way in which these systems interact?

**PRE**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=1 | is_correct=False

- [A] taking in oxygen and transporting it to cells of the body
- [B] releasing hormones and transporting them to cells of the body  [GT]
- [C] absorbing nutrients from food and transporting them to cells in the body  [PRED]
- [D] collecting waste products from the cells and transporting it out of the body

**POST**: acc=1 | acc_norm=0 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] taking in oxygen and transporting it to cells of the body
- [B] releasing hormones and transporting them to cells of the body  [PRED ,GT]
- [C] absorbing nutrients from food and transporting them to cells in the body
- [D] collecting waste products from the cells and transporting it out of the body

### doc_id=16

Q: As global temperatures increase, certain organisms will be more affected than others. The changes associated with global warming may result in an increase in sea level. Which organisms will be affected most as a result of the change in sea level?

**PRE**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] birds that eat fish from shallow waters  [PRED]
- [B] fish that live in coral reefs in shallow waters  [GT]
- [C] mammals that swim in cold, deep ocean waters
- [D] crustaceans at the bottom of deep sea ocean waters

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] birds that eat fish from shallow waters
- [B] fish that live in coral reefs in shallow waters  [PRED ,GT]
- [C] mammals that swim in cold, deep ocean waters
- [D] crustaceans at the bottom of deep sea ocean waters

### doc_id=23

Q: While on a movie set, a stuntman jumps off the roof of a building. As he falls toward an airbag, what is increasing?

**PRE**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=2 | is_correct=False

- [A] gravity
- [B] wind velocity
- [C] kinetic energy  [GT]
- [D] potential energy  [PRED]

**POST**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] gravity
- [B] wind velocity
- [C] kinetic energy  [PRED ,GT]
- [D] potential energy

### doc_id=26

Q: Which factor is most likely to cause the number of rabbits living in an area to increase?

**PRE**: acc=0 | acc_norm=1 | pred_idx=3 | correct_idx=1 | is_correct=False

- [1] less water
- [2] fewer predators  [GT]
- [3] lack of shelter
- [4] limited food  [PRED]

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [1] less water
- [2] fewer predators  [PRED ,GT]
- [3] lack of shelter
- [4] limited food

### doc_id=34

Q: Which two theories of Moon formation propose that much or all of the material comprising the Moon came from Earth?

**PRE**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=2 | is_correct=False

- [A] The Fission Theory and The Coaccretion Theory
- [B] The Coaccretion Theory and The Capture Theory
- [C] The Fission Theory and the Giant Impact Theory  [GT]
- [D] The Capture Theory and the Giant Impact Theory  [PRED]

**POST**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] The Fission Theory and The Coaccretion Theory
- [B] The Coaccretion Theory and The Capture Theory
- [C] The Fission Theory and the Giant Impact Theory  [PRED ,GT]
- [D] The Capture Theory and the Giant Impact Theory

### doc_id=45

Q: Darryl learns that freezing temperatures may help cause weathering. Which statement explains how freezing temperatures most likely cause weathering?

**PRE**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=3 | is_correct=False

- [A] by freezing the leaves on trees
- [B] by causing rocks to stick together  [PRED]
- [C] by turning acid rain into acid snow
- [D] by freezing water in the cracks of rocks  [GT]

**POST**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] by freezing the leaves on trees
- [B] by causing rocks to stick together
- [C] by turning acid rain into acid snow
- [D] by freezing water in the cracks of rocks  [PRED ,GT]

### doc_id=67

Q: A student suggests to the school board that they use a renewable energy source. The student suggests they use

**PRE**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=1 | is_correct=False

- [A] coal.
- [B] wind.  [GT]
- [C] wood.  [PRED]
- [D] natural gas.

**POST**: acc=1 | acc_norm=0 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] coal.
- [B] wind.  [PRED ,GT]
- [C] wood.
- [D] natural gas.

### doc_id=69

Q: Which human activity will help conserve Earth's natural resources?

**PRE**: acc=0 | acc_norm=1 | pred_idx=2 | correct_idx=1 | is_correct=False

- [A] leaving the television on all day
- [B] recycling plastic bottles  [GT]
- [C] cutting down trees  [PRED]
- [D] burning trash in the yard

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] leaving the television on all day
- [B] recycling plastic bottles  [PRED ,GT]
- [C] cutting down trees
- [D] burning trash in the yard

### doc_id=81

Q: Which of these traits is most influenced by environment?

**PRE**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] weight  [GT]
- [B] hair color  [PRED]
- [C] blood type
- [D] handedness

**POST**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] weight  [PRED ,GT]
- [B] hair color
- [C] blood type
- [D] handedness

### doc_id=82

Q: Which statement describes a characteristic of a gas that has a significant effect on the climates of both Earth and Venus?

**PRE**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] Nitrogen is chemically inert.  [PRED]
- [B] Sodium vapor reflects solar energy.
- [C] Carbon dioxide traps solar energy.  [GT]
- [D] Argon is unable to react with water.

**POST**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] Nitrogen is chemically inert.
- [B] Sodium vapor reflects solar energy.
- [C] Carbon dioxide traps solar energy.  [PRED ,GT]
- [D] Argon is unable to react with water.

### doc_id=88

Q: Clownfish take shelter in the tentacles of sea anemones and keep sea anemones clean. Which type of relationship does this represent?

**PRE**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] parasitism
- [B] commensalism  [PRED]
- [C] mutualism  [GT]
- [D] neutralism

**POST**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] parasitism
- [B] commensalism
- [C] mutualism  [PRED ,GT]
- [D] neutralism

### doc_id=106

Q: In their science classroom, Sam and Julia cross a heterozygous tall (Tt) pea plant with a homozygous short (tt) pea plant. What ratio represents the results Sam and Julia can expect?

**PRE**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] 1 tall plant to 3 short plants  [PRED]
- [B] 2 tall plants to 2 short plants  [GT]
- [C] 3 tall plants to 1 short plant
- [D] 4 tall plants to 0 short plants

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] 1 tall plant to 3 short plants
- [B] 2 tall plants to 2 short plants  [PRED ,GT]
- [C] 3 tall plants to 1 short plant
- [D] 4 tall plants to 0 short plants

### doc_id=111

Q: The elements that make up the atmosphere of Earth can be listed as percentages or can be shown in a graph. Which type of graph would best show this information?

**PRE**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] a bar graph  [PRED]
- [B] a pie chart  [GT]
- [C] a line graph
- [D] a scatterplot

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] a bar graph
- [B] a pie chart  [PRED ,GT]
- [C] a line graph
- [D] a scatterplot

### doc_id=123

Q: Topsoil is considered to be most fertile when it has a

**PRE**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] low pH level.
- [B] low sand content.  [PRED]
- [C] high organic matter level.  [GT]
- [D] high parent rock material level.

**POST**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] low pH level.
- [B] low sand content.
- [C] high organic matter level.  [PRED ,GT]
- [D] high parent rock material level.

### doc_id=176

Q: Lions tend to prey on primary consumers like zebras and gazelles. If there were a sudden decline in a population of lions, which ecological imbalance would most likely occur in the habitat?

**PRE**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] overgrazing  [GT]
- [B] eutrophication  [PRED]
- [C] invasion by non-native species
- [D] overproduction of greenhouse gases

**POST**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] overgrazing  [PRED ,GT]
- [B] eutrophication
- [C] invasion by non-native species
- [D] overproduction of greenhouse gases

### doc_id=186

Q: Which concept was most likely modified due to the invention of the microscope?

**PRE**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=1 | is_correct=False

- [A] size of subatomic particles
- [B] composition of living things  [GT]
- [C] number of the moons of Jupiter
- [D] formation of sedimentary rocks  [PRED]

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] size of subatomic particles
- [B] composition of living things  [PRED ,GT]
- [C] number of the moons of Jupiter
- [D] formation of sedimentary rocks

### doc_id=193

Q: Which is the function of the gallbladder?

**PRE**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] store bile  [GT]
- [B] produce bile  [PRED]
- [C] store digestive enzymes
- [D] produce digestive enzymes

**POST**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] store bile  [PRED ,GT]
- [B] produce bile
- [C] store digestive enzymes
- [D] produce digestive enzymes

### doc_id=199

Q: During which process do animals increase in size?

**PRE**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] breathing  [PRED]
- [B] growing  [GT]
- [C] shedding
- [D] repairing

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] breathing
- [B] growing  [PRED ,GT]
- [C] shedding
- [D] repairing

## Degradations (PRE correct → POST incorrect), top 20

### doc_id=6

Q: A student has just completed a laboratory activity. What is the last action that the student should perform before leaving the lab area?

**PRE**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] wash hands  [PRED ,GT]
- [B] turn off all equipment
- [C] put away all glassware
- [D] wash instruments and table tops

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] wash hands  [GT]
- [B] turn off all equipment  [PRED]
- [C] put away all glassware
- [D] wash instruments and table tops

### doc_id=298

Q: Which of the following lists units of length from smallest to largest?

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] light-year, astronomical unit, kilometer, angstrom
- [B] angstrom, kilometer, astronomical unit, light-year  [PRED ,GT]
- [C] astronomical unit, angstrom, kilometer, light-year
- [D] kilometer, angstrom, light-year, astronomical unit

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] light-year, astronomical unit, kilometer, angstrom  [PRED]
- [B] angstrom, kilometer, astronomical unit, light-year  [GT]
- [C] astronomical unit, angstrom, kilometer, light-year
- [D] kilometer, angstrom, light-year, astronomical unit

### doc_id=316

Q: What can be inferred from a food product advertisement that claims "30% less fat than our leading competitors"?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] It is a sugar-free product.
- [B] It will help a person lose weight.
- [C] It is the healthiest choice available.
- [D] The fat content of the item is reduced.  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=3 | is_correct=False

- [A] It is a sugar-free product.  [PRED]
- [B] It will help a person lose weight.
- [C] It is the healthiest choice available.
- [D] The fat content of the item is reduced.  [GT]

### doc_id=326

Q: Today, almost all cars have seat belts. How does improving the design of seat belts help people the most?

**PRE**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] It decreases the cost of cars.
- [B] It increases the speed at which cars can travel.
- [C] It decreases injuries to passengers in cars.  [PRED ,GT]
- [D] It increases the comfort of passengers in cars.

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=2 | is_correct=False

- [A] It decreases the cost of cars.
- [B] It increases the speed at which cars can travel.
- [C] It decreases injuries to passengers in cars.  [GT]
- [D] It increases the comfort of passengers in cars.  [PRED]

### doc_id=423

Q: A coach is standing at the finish line of a race. He is holding a stopwatch. What is the coach most likely measuring with the stopwatch?

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] the time of day
- [B] the distance of the race
- [C] the time it took to run the race  [PRED ,GT]
- [D] the number of steps taken by the runners

**POST**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] the time of day
- [B] the distance of the race  [PRED]
- [C] the time it took to run the race  [GT]
- [D] the number of steps taken by the runners

### doc_id=450

Q: Use the information below to answer the question. Manufacturing uses many steps to change natural resources into products. Some of these steps change natural resources into industrial materials. These steps are called primary processes. All of the following are primary processes except

**PRE**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] melting iron ore.
- [B] producing lumber.
- [C] molding plastic.  [PRED ,GT]
- [D] crushing rock into gravel.

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] melting iron ore.  [PRED]
- [B] producing lumber.
- [C] molding plastic.  [GT]
- [D] crushing rock into gravel.

### doc_id=489

Q: When a small group of organisms colonizes a new habitat, the population may be genetically different from the parent population due to differences in allele frequencies. The process responsible for this is

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] natural selection.
- [B] disruptive selection.
- [C] genetic drift.  [PRED ,GT]
- [D] genetic equilibrium.

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] natural selection.  [PRED]
- [B] disruptive selection.
- [C] genetic drift.  [GT]
- [D] genetic equilibrium.

### doc_id=497

Q: Which sequence has the states of matter listed from least to greatest kinetic energy?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] solid -> gas -> liquid
- [B] gas -> liquid -> solid
- [C] liquid -> solid -> gas
- [D] solid -> liquid -> gas  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=3 | is_correct=False

- [A] solid -> gas -> liquid
- [B] gas -> liquid -> solid  [PRED]
- [C] liquid -> solid -> gas
- [D] solid -> liquid -> gas  [GT]

### doc_id=521

Q: When tectonic plates move, they can form different landforms. Which is least likely to be associated with the tectonic plate movement that forms volcanoes?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] hot spot
- [B] rift valley
- [C] subduction zone
- [D] transform boundary  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=3 | is_correct=False

- [A] hot spot
- [B] rift valley  [PRED]
- [C] subduction zone
- [D] transform boundary  [GT]

### doc_id=546

Q: When buying a sunscreen, which is the best question to keep in mind while reading the label for maximum effectiveness?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] What is the cost per ounce?
- [B] Who is the manufacturer?
- [C] Is the product waterproof?
- [D] How much protection does it provide?  [PRED ,GT]

**POST**: acc=0 | acc_norm=1 | pred_idx=2 | correct_idx=3 | is_correct=False

- [A] What is the cost per ounce?
- [B] Who is the manufacturer?
- [C] Is the product waterproof?  [PRED]
- [D] How much protection does it provide?  [GT]

### doc_id=639

Q: A full Moon is observed in Buffalo, New York, on June 1. Approximately when will the next full Moon be observed in Buffalo?

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [1] June 7
- [2] June 15
- [3] July 1  [PRED ,GT]
- [4] July 7

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=2 | is_correct=False

- [1] June 7
- [2] June 15  [PRED]
- [3] July 1  [GT]
- [4] July 7

### doc_id=816

Q: In a recycling program, people can separate paper from their other trash. The paper is sent to factories and turned into new products. What does paper recycling help conserve the most?

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] air
- [B] gasoline
- [C] trees  [PRED ,GT]
- [D] water

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=2 | is_correct=False

- [A] air
- [B] gasoline
- [C] trees  [GT]
- [D] water  [PRED]

### doc_id=982

Q: Jon had a flat tire on his car. He used a hydraulic jack to lift the car up so that he could change the tire. If Jon knows the amount of force used to lift the car 0.25 meter off of the ground, what is he able to calculate?

**PRE**: acc=1 | acc_norm=0 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] momentum
- [B] power
- [C] pressure
- [D] work  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=3 | is_correct=False

- [A] momentum
- [B] power
- [C] pressure  [PRED]
- [D] work  [GT]

### doc_id=1117

Q: The following advertisement was placed in the window of a camping supply store. "The double-thermal 'Polar Snooze' sleeping bag is here! It will keep you warm for winter camping!" Based on this advertisement, the best conclusion about Polar Snooze sleeping bags is that they

**PRE**: acc=1 | acc_norm=0 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] are lightweight.
- [B] have insulation.  [PRED ,GT]
- [C] make winter camping easy.
- [D] cost less than other sleeping bags.

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] are lightweight.  [PRED]
- [B] have insulation.  [GT]
- [C] make winter camping easy.
- [D] cost less than other sleeping bags.

### doc_id=1160

Q: Which of these best describes a tornado?

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] A winter storm that produces frozen precipitation
- [B] A rotating funnel-shaped cloud with strong winds and thunderstorms  [PRED ,GT]
- [C] A severe weather condition with low temperatures and blowing snow
- [D] A storm that forms over warm ocean water and has extremely strong winds

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] A winter storm that produces frozen precipitation  [PRED]
- [B] A rotating funnel-shaped cloud with strong winds and thunderstorms  [GT]
- [C] A severe weather condition with low temperatures and blowing snow
- [D] A storm that forms over warm ocean water and has extremely strong winds

### doc_id=1167

Q: A scientist wants to track contaminant movement in the Gulf Stream. The Gulf Stream is a warm water current in the North Atlantic Ocean and is part of the North Atlantic gyre. The gyre is influenced by the Coriolis effect. To follow the contaminant after it exits the Gulf Stream, the scientist needs to know characteristics of the North Atlantic gyre. Which of these best describes a movement of the North Atlantic gyre the scientist needs to know?

**PRE**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] linear movement due west
- [B] linear movement due south
- [C] clockwise movement  [PRED ,GT]
- [D] counterclockwise movement

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=2 | is_correct=False

- [A] linear movement due west
- [B] linear movement due south
- [C] clockwise movement  [GT]
- [D] counterclockwise movement  [PRED]

### doc_id=1227

Q: A bird called a ptarmigan has feathered feet. The feathers on the feet of the ptarmigan are most helpful when this bird ___.

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] digs up food
- [B] walks in deep snow  [PRED ,GT]
- [C] climbs rocky cliffs
- [D] runs under bushes

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] digs up food  [PRED]
- [B] walks in deep snow  [GT]
- [C] climbs rocky cliffs
- [D] runs under bushes

### doc_id=1258

Q: Which material has the least resistance to the flow of electricity?

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] rubber
- [B] aluminum  [PRED ,GT]
- [C] granite
- [D] wood

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] rubber  [PRED]
- [B] aluminum  [GT]
- [C] granite
- [D] wood

### doc_id=1409

Q: Which of these shows the correct order needed for a solar eclipse to happen?

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] Sun, Earth, Moon
- [B] Sun, Moon, Earth  [PRED ,GT]
- [C] Moon, Sun, Earth
- [D] Moon, Earth, Sun

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=1 | is_correct=False

- [A] Sun, Earth, Moon
- [B] Sun, Moon, Earth  [GT]
- [C] Moon, Sun, Earth
- [D] Moon, Earth, Sun  [PRED]

### doc_id=1423

Q: Why do multicellular organisms need transport systems?

**PRE**: acc=1 | acc_norm=1 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] Most have cells that are not able to exchange gases with the outside environment.  [PRED ,GT]
- [B] Most have cells that are unable to grow and survive in their environment.
- [C] Most have cells that need food from sources outside their environment.
- [D] Most have cells that require more energy to survive than single-celled organisms.

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=0 | is_correct=False

- [A] Most have cells that are not able to exchange gases with the outside environment.  [GT]
- [B] Most have cells that are unable to grow and survive in their environment.
- [C] Most have cells that need food from sources outside their environment.
- [D] Most have cells that require more energy to survive than single-celled organisms.  [PRED]
