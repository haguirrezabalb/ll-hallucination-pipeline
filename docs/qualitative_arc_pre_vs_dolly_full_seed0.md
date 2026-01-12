# Qualitative cases - ARC-Easy (seed0) - baseline vs dolly_full

- Baseline samples: `evals/baseline/baseline_arc_easy_seed0/__home__USER__models__qwen3-8b-base__Qwen3-8B-Base/samples_arc_easy_2026-01-09T23-57-41.041908.jsonl`

- Post (dolly_full) samples: `evals/postqlora/by_adapter/dolly_full/arc_easy_seed0/samples_arc_easy_2026-01-10T10-46-56.000227.jsonl`

Selection criterion:

- Correct/incorrect is based on `acc` (unnormalized loglikelihood argmax over choices).
- `acc_norm` is reported for context and may disagree with `acc`.

## Improvements (PRE incorrect → POST correct), top 20

### doc_id=1

Q: Which piece of safety equipment is used to keep mold spores from entering the respiratory system?

**PRE**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] safety goggles  [PRED]
- [B] breathing mask  [GT]
- [C] rubber gloves
- [D] lead apron

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] safety goggles
- [B] breathing mask  [PRED ,GT]
- [C] rubber gloves
- [D] lead apron

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

### doc_id=20

Q: A research scientist writes a paper on the initial regrowth of a forest after a fire has damaged the entire ecosystem. Which title would be best for the paper?

**PRE**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=3 | is_correct=False

- [A] Primary Succession  [PRED]
- [B] Stable Communities
- [C] Climax Communities
- [D] Secondary Succession  [GT]

**POST**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] Primary Succession
- [B] Stable Communities
- [C] Climax Communities
- [D] Secondary Succession  [PRED ,GT]

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

### doc_id=51

Q: Planets outside of our solar system have been detected. What suggested the presence of a planet outside of our solar system?

**PRE**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] radio wave emissions  [PRED]
- [B] a wobble in the rotation of the star  [GT]
- [C] regular occurring eclipses of its moons
- [D] the discovery of a star as large as our own

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] radio wave emissions
- [B] a wobble in the rotation of the star  [PRED ,GT]
- [C] regular occurring eclipses of its moons
- [D] the discovery of a star as large as our own

### doc_id=60

Q: During which activity should a student wear goggles?

**PRE**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=1 | is_correct=False

- [A] writing a science report
- [B] mixing baking soda with water  [GT]
- [C] measuring the length of a shadow
- [D] examining a leaf with a microscope  [PRED]

**POST**: acc=1 | acc_norm=0 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] writing a science report
- [B] mixing baking soda with water  [PRED ,GT]
- [C] measuring the length of a shadow
- [D] examining a leaf with a microscope

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

### doc_id=95

Q: Through which activity do animals get the carbon that is needed for their bodies?

**PRE**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] eating  [GT]
- [B] breathing  [PRED]
- [C] running
- [D] sleeping

**POST**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] eating  [PRED ,GT]
- [B] breathing
- [C] running
- [D] sleeping

### doc_id=100

Q: Which of the following is more likely to occur in a plant cell than in an animal cell?

**PRE**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=1 | is_correct=False

- [A] synthesis of enzymes
- [B] formation of cellulose  [GT]
- [C] breakdown of glucose  [PRED]
- [D] active transport of ions

**POST**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] synthesis of enzymes
- [B] formation of cellulose  [PRED ,GT]
- [C] breakdown of glucose
- [D] active transport of ions

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

### doc_id=167

Q: Which is the best way to help prevent the flu from becoming a pandemic?

**PRE**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=0 | is_correct=False

- [A] getting a vaccination  [GT]
- [B] taking antibiotics
- [C] eating fruits and vegetables
- [D] washing hands often  [PRED]

**POST**: acc=1 | acc_norm=1 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] getting a vaccination  [PRED ,GT]
- [B] taking antibiotics
- [C] eating fruits and vegetables
- [D] washing hands often

## Degradations (PRE correct → POST incorrect), top 20

### doc_id=13

Q: Which of these will most likely harm a habitat?

**PRE**: acc=1 | acc_norm=1 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] planting trees
- [B] water pollution  [PRED ,GT]
- [C] rainfall
- [D] sunlight

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=1 | is_correct=False

- [A] planting trees  [PRED]
- [B] water pollution  [GT]
- [C] rainfall
- [D] sunlight

### doc_id=231

Q: The rover Spirit is a robotic probe that NASA has placed on Mars. The gravitational attraction of Mars is approximately 62% less than that of Earth. Compared to its measurements on Earth, on Mars the probe has

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] the same weight and the same mass.
- [B] a larger weight, but smaller mass.
- [C] a smaller mass and larger weight.
- [D] a smaller weight and the same mass.  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=3 | is_correct=False

- [A] the same weight and the same mass.  [PRED]
- [B] a larger weight, but smaller mass.
- [C] a smaller mass and larger weight.
- [D] a smaller weight and the same mass.  [GT]

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

### doc_id=301

Q: Which of these events during a storm at sea can add oxygen from the atmosphere to ocean water?

**PRE**: acc=1 | acc_norm=0 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] high winds  [PRED ,GT]
- [B] lightning
- [C] pressure change
- [D] temperature change

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] high winds  [GT]
- [B] lightning  [PRED]
- [C] pressure change
- [D] temperature change

### doc_id=316

Q: What can be inferred from a food product advertisement that claims "30% less fat than our leading competitors"?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] It is a sugar-free product.
- [B] It will help a person lose weight.
- [C] It is the healthiest choice available.
- [D] The fat content of the item is reduced.  [PRED ,GT]

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=3 | is_correct=False

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

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] It decreases the cost of cars.
- [B] It increases the speed at which cars can travel.  [PRED]
- [C] It decreases injuries to passengers in cars.  [GT]
- [D] It increases the comfort of passengers in cars.

### doc_id=339

Q: Which of the following is performed by the quality control division of a company that is manufacturing a chair?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] applying the varnish
- [B] assembling the parts
- [C] cutting the material
- [D] inspecting the finish  [PRED ,GT]

**POST**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=3 | is_correct=False

- [A] applying the varnish
- [B] assembling the parts  [PRED]
- [C] cutting the material
- [D] inspecting the finish  [GT]

### doc_id=450

Q: Use the information below to answer the question. Manufacturing uses many steps to change natural resources into products. Some of these steps change natural resources into industrial materials. These steps are called primary processes. All of the following are primary processes except

**PRE**: acc=1 | acc_norm=0 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] melting iron ore.
- [B] producing lumber.
- [C] molding plastic.  [PRED ,GT]
- [D] crushing rock into gravel.

**POST**: acc=0 | acc_norm=0 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] melting iron ore.
- [B] producing lumber.  [PRED]
- [C] molding plastic.  [GT]
- [D] crushing rock into gravel.

### doc_id=521

Q: When tectonic plates move, they can form different landforms. Which is least likely to be associated with the tectonic plate movement that forms volcanoes?

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] hot spot
- [B] rift valley
- [C] subduction zone
- [D] transform boundary  [PRED ,GT]

**POST**: acc=0 | acc_norm=0 | pred_idx=2 | correct_idx=3 | is_correct=False

- [A] hot spot
- [B] rift valley
- [C] subduction zone  [PRED]
- [D] transform boundary  [GT]

### doc_id=524

Q: All of the following are renewable resources except

**PRE**: acc=1 | acc_norm=1 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] minerals.  [PRED ,GT]
- [B] trees.
- [C] wind.
- [D] water.

**POST**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=0 | is_correct=False

- [A] minerals.  [GT]
- [B] trees.  [PRED]
- [C] wind.
- [D] water.

### doc_id=529

Q: Electrical energy is best described as

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] coming from the Sun.
- [B] attracting objects.
- [C] moving negative charges.  [PRED ,GT]
- [D] developing radiation.

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] coming from the Sun.  [PRED]
- [B] attracting objects.
- [C] moving negative charges.  [GT]
- [D] developing radiation.

### doc_id=576

Q: Scientists think that the rise in global temperature during the last one hundred years is due to an increase of carbon dioxide in the atmosphere. Which question would best help scientists assess the claim that humans are responsible for the rising global temperature?

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] What is the mechanism by which carbon dioxide heats Earth?
- [B] What is the source of most of the carbon dioxide in the atmosphere?
- [C] What is the source of the increase of carbon dioxide in the atmosphere?  [PRED ,GT]
- [D] What is the increase in the concentration of carbon dioxide in the atmosphere?

**POST**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=2 | is_correct=False

- [A] What is the mechanism by which carbon dioxide heats Earth?
- [B] What is the source of most of the carbon dioxide in the atmosphere?  [PRED]
- [C] What is the source of the increase of carbon dioxide in the atmosphere?  [GT]
- [D] What is the increase in the concentration of carbon dioxide in the atmosphere?

### doc_id=580

Q: One hot summer, a grassland experienced a drought. Which most likely happened in the ecosystem during this time?

**PRE**: acc=1 | acc_norm=1 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] The competition for food among primary consumers increased.  [PRED ,GT]
- [B] Nutrients cycled through the system at a faster rate.
- [C] Less solar radiation was able to enter the system.
- [D] Secondary consumers became extinct.

**POST**: acc=0 | acc_norm=1 | pred_idx=3 | correct_idx=0 | is_correct=False

- [A] The competition for food among primary consumers increased.  [GT]
- [B] Nutrients cycled through the system at a faster rate.
- [C] Less solar radiation was able to enter the system.
- [D] Secondary consumers became extinct.  [PRED]

### doc_id=774

Q: Making aluminum cans from recycled materials instead of raw materials is a wise choice because it

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] saves time.
- [B] saves trees.
- [C] creates energy.
- [D] reduces pollution.  [PRED ,GT]

**POST**: acc=0 | acc_norm=1 | pred_idx=1 | correct_idx=3 | is_correct=False

- [A] saves time.
- [B] saves trees.  [PRED]
- [C] creates energy.
- [D] reduces pollution.  [GT]

### doc_id=807

Q: On a field trip in a wooded area, you see a small, strange object. You wonder whether is is a live animal. The best way to find out is to observe the object to see if it

**PRE**: acc=1 | acc_norm=1 | pred_idx=3 | correct_idx=3 | is_correct=True

- [A] has an odor.
- [B] has separate parts.
- [C] can make a noise and has a lifelike color.
- [D] carries out basic life functions.  [PRED ,GT]

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=3 | is_correct=False

- [A] has an odor.  [PRED]
- [B] has separate parts.
- [C] can make a noise and has a lifelike color.
- [D] carries out basic life functions.  [GT]

### doc_id=910

Q: Deposition of sediment will most likely form a

**PRE**: acc=1 | acc_norm=0 | pred_idx=1 | correct_idx=1 | is_correct=True

- [A] cave.
- [B] delta.  [PRED ,GT]
- [C] river.
- [D] mountain.

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=1 | is_correct=False

- [A] cave.
- [B] delta.  [GT]
- [C] river.
- [D] mountain.  [PRED]

### doc_id=1003

Q: Which characteristic does a euglena share with an amoeba?

**PRE**: acc=1 | acc_norm=1 | pred_idx=0 | correct_idx=0 | is_correct=True

- [A] They reproduce by mitosis.  [PRED ,GT]
- [B] They eat by phagocytosis.
- [C] They respond to light stimuli.
- [D] They move by changing shape.

**POST**: acc=0 | acc_norm=0 | pred_idx=3 | correct_idx=0 | is_correct=False

- [A] They reproduce by mitosis.  [GT]
- [B] They eat by phagocytosis.
- [C] They respond to light stimuli.
- [D] They move by changing shape.  [PRED]

### doc_id=1035

Q: A pan containing hot water is left on the counter and becomes cool mainly due to

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] water molecules moving apart.
- [B] cold air penetrating the hot water.
- [C] heat from the water moving into the cooler air.  [PRED ,GT]
- [D] hot water reacting with the metal pan.

**POST**: acc=0 | acc_norm=1 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] water molecules moving apart.  [PRED]
- [B] cold air penetrating the hot water.
- [C] heat from the water moving into the cooler air.  [GT]
- [D] hot water reacting with the metal pan.

### doc_id=1084

Q: When an electric fan is running, most of the incoming electrical energy changes into which kind of energy?

**PRE**: acc=1 | acc_norm=1 | pred_idx=2 | correct_idx=2 | is_correct=True

- [A] heat energy
- [B] light energy
- [C] mechanical energy  [PRED ,GT]
- [D] sound energy

**POST**: acc=0 | acc_norm=0 | pred_idx=0 | correct_idx=2 | is_correct=False

- [A] heat energy  [PRED]
- [B] light energy
- [C] mechanical energy  [GT]
- [D] sound energy

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
