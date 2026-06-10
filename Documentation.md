# Documentation

## 1. Libraries Used
- pygame — Used for rendering, input handling, audio, and the main game loop.
- sys — Exit and process control for quitting and restarting the app.
- os — Filesystem operations for loading assets and saving per-user data.
- random — Randomization for occasional events and mission layout.
- json — Read/write JSON save files (save.json, diary.json, finance.json).
- datetime — Timestamping diary entries and era summaries.
- copy — Deep copying data for custom reports and non-destructive simulations.

## 2. Assets & Templates

### Backgrounds
Background images are in assets/backgrounds. Era-specific background files are named by era (e.g., egypt.png, greece.png). A home.png and mission_bg.png are also present for the start and mission screens.

### Pet Sprites
Pet sprites are organized by species under assets/pets/{species}/ and use the naming pattern {species}_{mood}.png (e.g., dog_happy.png, dog_sick.png). Mood-specific sprites include happy, sad, sick, energetic (if present), and neutral fallbacks.

### Item Images
Item images for era actions and missions are found in assets/items and assets/pets/images; filenames reflect era and item (e.g., egypt_bread.png, modern_game.png).

### Player Avatars
Player avatar images are in assets/player (boy1.png, girl1.png, boy2.png, girl2.png). The customization screen labels them Alex, Maria, Carlos, and Grace respectively.

### Fonts
The game uses system fonts via pygame.font.SysFont (e.g., Arial, bold variants, different sizes).

## 3. Data Files
- save.json: stores current era, unlocked eras, and pet state. Read on game load, written on game quit and era transition. (Now stored per-user under data/{username}/save.json.)
- diary.json: stores every action the player takes as a timestamped log. Written on every action, read when the diary screen opens. (Now stored per-user under data/{username}/diary.json.)
- finance.json: stores spending totals by category and by era. Written on every purchase, read when the financial summary screen opens. (Now stored per-user under data/{username}/finance.json.)
- era_summaries.json: stores the end-of-era summary data shown in the era completion popup. Written when an era is completed. (Now stored per-user under data/{username}/era_summaries.json when applicable.)

## 4. External Research Sources
1. American Veterinary Medical Association (AVMA) — Pet nutrition guidelines, preventative care. Citation: www.avma.org/resources-tools/pet-owners/petcare
2. ASPCA (American Society for the Prevention of Cruelty to Animals) — Feeding schedules, behavioral health. Citation: www.aspca.org/pet-care
3. Humane Society of the United States — Costs of pet ownership. Citation: www.humanesociety.org
4. American Kennel Club (AKC) — Dog care fundamentals. Citation: www.akc.org/expert-advice/health
5. ASPCA Annual Pet Care Costs — Pet care costs. Citation: www.aspca.org/pet-care/pet-care-costs
6. U.S. Bureau of Labor Statistics (BLS) — Consumer spending on pets. Citation: www.bls.gov
7. Smithsonian National Museum of Natural History — Daily life in Ancient Egypt. Citation: www.si.edu
8. BBC Bitesize — Industrial Revolution living standards. Citation: bbc.co.uk/bitesize
9. National Geographic — Historical context and images. Citation: nationalgeographic.com

## 5. Image Attributions

### Historical & Architecture Images
1️⃣ Egypt Tours Portal
Image of Ancient Egypt landmarks and architecture
Citation: Egypt Tours Portal. “Ancient Egypt.” www.egypttoursportal.com/en-us/egypt/

2️⃣ Exodus Travels
Image of Ancient Greece historical sites
Citation: Exodus Travels. “Highlights of Ancient Greece.” www.exodustravels.com/us/trips/greece-holidays/culture/highlights-of-ancient-greece/agm

3️⃣ Medievalists.net
Image representing Ancient Rus and early medieval Europe
Citation: Medievalists.net. “Ancient Rus and Medieval Europe: The Emergence of Early Medieval States.” www.medieval.eu/ancient-rus-and-medieval-europe-the-emergence-of-early-medieval-states/

4️⃣ History Hit
Industrial Revolution invention imagery
Citation: History Hit. “Key Inventions of the Industrial Revolution.” www.historyhit.com/key-inventions-of-the-industrial-revolution/

5️⃣ The Metropolitan Museum of Art
Image of papyrus in Ancient Egypt
Citation: The Metropolitan Museum of Art. “Papyrus in Ancient Egypt.” www.metmuseum.org/essays/papyrus-in-ancient-egypt

6️⃣ Egypt Tours Portal (Blog)
Image of Ancient Egyptian furniture
Citation: Egypt Tours Portal. “Ancient Egyptian Furniture.” www.egypttoursportal.com/en-us/blog/ancient-egyptian-civilization/ancient-egyptian-furniture/

7️⃣ U.S. National Library of Medicine
Image related to Ancient Greek medicine
Citation: U.S. National Library of Medicine. “Greek Medicine.” www.nlm.nih.gov/hmd/topics/greek-medicine/index.html

### Resources & Materials Images

8️⃣ Stockholm International Water Institute
Image representing importance of water
Citation: Stockholm International Water Institute. “Why Is Water Important?” siwi.org/whywater/why-is-water-important/

9️⃣ ThoughtCo
Coal imagery
Citation: ThoughtCo. “All About Coal.” www.thoughtco.com/all-about-coal-1440944

🔟 HowStuffWorks
Types of wood imagery
Citation: HowStuffWorks. “Types of Wood.” home.howstuffworks.com/types-of-wood.htm

1️⃣1️⃣ Brick My Walls
Brick material image
Citation: Brick My Walls. “Old Red MR02.;” www.brickmywalls.com/shop-online/old-red-mr02/

1️⃣2️⃣ Vecteezy
Gear icon illustration
Citation: Vecteezy. “Gear Icon.” www.vecteezy.com/free-vector/gear-icon

1️⃣3️⃣ iStock
Olympic medal illustration
Citation: iStock. “Olympic Medal Illustrations.” www.istockphoto.com

### Food & Agriculture Images

1️⃣4️⃣ The Spruce Eats
Bread image
Citation: The Spruce Eats. “Sour Cream White Bread.” www.thespruceeats.com/sour-cream-white-bread-428178

1️⃣5️⃣ Epicurious
Fresh herbs image
Citation: Epicurious. “Types of Fresh Herbs.” www.epicurious.com/ingredients/types-of-fresh-herbs

1️⃣6️⃣ Four Winds Growers
Flame seedless grape vine image
Citation: Four Winds Growers. “Flame Seedless Grape Vine.” www.fourwindsgrowers.com/products/flame-seedless-grape-vine

### Graphics & Illustrations

1️⃣7️⃣ Freepik
Grey boulder rock graphic
Citation: Freepik. “Grey Boulder Rock Isolated on Transparent Background.” www.freepik.com

1️⃣8️⃣ Shutterstock
Happy and sad dog vector images
Citation: Shutterstock. “Happy Dog Sad Dog.” www.shutterstock.com

1️⃣9️⃣ VectorStock
Cartoon cat emotion illustrations
Citation: VectorStock. “Cartoon Cat Faces with Emotions.” www.vectorstock.com

2️⃣0️⃣ Adobe Stock
Cartoon pigeon emotion illustration
Citation: Adobe Stock. “Cartoon Pigeon Funny Bird Character.” stock.adobe.com

2️⃣1️⃣ Alamy
White bunny emotion illustration
Citation: Alamy. “White Bunny with Different Emotions Illustration.” www.alamy.com

### Miscellaneous Product Images

2️⃣2️⃣ Vital Sounds
Gertie Ball product image
Citation: Vital Sounds. “Gertie Ball.” www.vitalsounds.com/product/gertie-ball/

2️⃣3️⃣ FFXIV Housing
Decorative in-game item image
Citation: FFXIV Housing. “Item View.” en.ff14housing.com/itemview.php

2️⃣4️⃣ Doodlewash
Magic potion illustration
Citation: Doodlewash. “A Magic Potion.” www.doodlewash.com/a-magic-potion/

2️⃣5️⃣ Amazon
Wooden magical wand product image
Citation: Amazon. “Handicraftviet Wooden Collectible Cosplay Magical Wand.” www.amazon.com

2️⃣6️⃣ BestRide
Motor vs. engine illustration
Citation: BestRide. “Should You Call It a Motor or an Engine?” blog.bestride.com

2️⃣7️⃣ Math N Stuff
Sample essay image
Citation: Math N Stuff. “Here Is a Sample Essay.” www.mathnstuff.com/math/spoken/here/3essay/egraf.htm

## 6. AI/ML Component
The game includes a machine learning tip system implemented in pet_ml.py through the PetML class. On every game frame, PetML evaluates the pet's current stats (hunger, happiness, energy, health), the player's current ChronoCoin balance, and the player's recent spending history. Based on conditional rules that weight the most critically low stat, it generates a plain-language suggestion displayed above the action buttons — for example, "Your pet is hungry — consider feeding soon" or "You're running low on coins — prioritize essential care." The system is called ML because it takes multiple dynamic input variables and produces a personalized, context-sensitive output recommendation, similar in structure to a rule-based recommendation engine.