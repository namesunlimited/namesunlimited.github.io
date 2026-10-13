/* Names Unlimited - name database
   Curated lists of genuine, commonly used first and last names.
   Not tied to any real, specific individual when combined. */

const NAMES_DB = {
  male: [
    "Liam","Noah","Oliver","James","Elijah","William","Henry","Lucas","Benjamin","Theodore",
    "Mason","Michael","Ethan","Alexander","Daniel","Jacob","Logan","Jackson","Sebastian","Aiden",
    "Matthew","Samuel","David","Joseph","Carter","Owen","Wyatt","John","Jack","Luke",
    "Jayden","Dylan","Grayson","Levi","Isaac","Gabriel","Julian","Mateo","Anthony","Jaxon",
    "Lincoln","Joshua","Christopher","Andrew","Thomas","Caleb","Ryan","Nathan","Adrian","Charles",
    "Aaron","Cameron","Hunter","Christian","Eli","Jonathan","Connor","Landon","Colton","Jeremiah",
    "Ezra","Nolan","Jose","Angel","Ian","Austin","Adam","Elias","Jaxson","Greyson",
    "Bennett","Carson","Robert","Xavier","Leo","Asher","Jordan","Dominic","Brooks","Silas",
    "George","Emmett","Alex","Josiah","Kai","Roman","Miles","Vincent","Weston","Amir",
    "Everett","Rowan","Micah","Gael","Beau","Damian","August","Maxwell","Enzo","Karim",
    "Arjun","Devansh","Rohan","Aarav","Vivaan","Kabir","Rahul","Aditya","Ravi","Sanjay",
    "Diego","Mateus","Luca","Matteo","Hiroshi","Kenji","Wei","Chen","Jun","Sung"
  ],
  female: [
    "Olivia","Emma","Charlotte","Amelia","Sophia","Isabella","Ava","Mia","Evelyn","Luna",
    "Harper","Camila","Sofia","Scarlett","Elizabeth","Eleanor","Emily","Chloe","Mila","Violet",
    "Penelope","Gianna","Aria","Abigail","Ella","Avery","Hazel","Nora","Layla","Lily",
    "Addison","Zoey","Victoria","Aubrey","Grace","Riley","Nova","Stella","Natalie","Zoe",
    "Leah","Hannah","Paisley","Skylar","Everly","Aurora","Savannah","Brooklyn","Bella","Claire",
    "Kinsley","Naomi","Ellie","Sarah","Genesis","Madelyn","Ariana","Ruby","Alice","Lucy",
    "Maya","Sadie","Willow","Anna","Delilah","Josephine","Aaliyah","Madison","Piper","Athena",
    "Peyton","Quinn","Autumn","Isla","Eden","Melanie","Adeline","Serenity","Alina","Wren",
    "Julia","Vivian","Kennedy","Iris","Mackenzie","Faith","Reagan","Molly","Rosalie","Valeria",
    "June","Sophie","Aubree","Josie","Elena","Katherine","Alexandra","Cora","Freya","Margaret",
    "Priya","Ananya","Diya","Kavya","Ishita","Meera","Aditi","Sana","Zara","Aisha",
    "Camille","Isabelle","Yui","Sakura","Mei","Ling","Ji-woo","Fatima","Layan","Noor"
  ],
  last: [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
    "Sharma","Gupta","Verma","Khan","Chowdhury","Das","Rao","Iyer","Reddy","Kapoor",
    "Nakamura","Tanaka","Kobayashi","Wang","Zhang","Liu","Park","Choi","Muller","Rossi"
  ]
};

const USERNAME_SUFFIXES = ["", "", "", "_", "", "x", "_x", "", "official", "hq", "", "22", "07", "88", "", "tv", "", "co"];

function pick(arr){ return arr[Math.floor(Math.random() * arr.length)]; }

function randomFirst(gender){
  if(gender === "male") return pick(NAMES_DB.male);
  if(gender === "female") return pick(NAMES_DB.female);
  return pick(Math.random() < 0.5 ? NAMES_DB.male : NAMES_DB.female);
}

function randomLast(){ return pick(NAMES_DB.last); }

function generateNameList({ type = "full", gender = "both", count = 50 }){
  const out = [];
  const seen = new Set();
  const maxAttempts = count * 20;
  let attempts = 0;
  while(out.length < count && attempts < maxAttempts){
    attempts++;
    let name;
    if(type === "first"){ name = randomFirst(gender); }
    else if(type === "last"){ name = randomLast(); }
    else { name = `${randomFirst(gender)} ${randomLast()}`; }
    const key = name.toLowerCase();
    if(seen.has(key) && count <= (type === "last" ? NAMES_DB.last.length : 200)) continue;
    seen.add(key);
    out.push(name);
  }
  return out;
}

function generateUsernameList(count = 50){
  const out = [];
  const seen = new Set();
  let attempts = 0;
  while(out.length < count && attempts < count * 20){
    attempts++;
    const first = randomFirst("both").toLowerCase();
    const last = randomLast().toLowerCase();
    const style = Math.floor(Math.random() * 4);
    let uname;
    if(style === 0) uname = `${first}${last}${pick(USERNAME_SUFFIXES)}`;
    else if(style === 1) uname = `${first}.${last}${pick(USERNAME_SUFFIXES)}`;
    else if(style === 2) uname = `${first}_${last.slice(0,4)}${Math.floor(Math.random()*99)}`;
    else uname = `the.${first}${Math.floor(Math.random()*999)}`;
    if(seen.has(uname)) continue;
    seen.add(uname);
    out.push(uname);
  }
  return out;
}

/* ---- Additional generators (Japanese, Elf, Band, City, School) ----
   Appended without modifying anything above; existing tools are unaffected. */

const JAPANESE_DB = {
  male: [
    "Haruto","Yuto","Sota","Yuki","Hayato","Ren","Kaito","Sora","Riku","Itsuki",
    "Minato","Asahi","Aoi","Yamato","Kenta","Takumi","Shota","Daiki","Ryota","Kenji",
    "Hiroshi","Kazuki","Naoki","Tatsuya","Yosuke","Masaru","Isamu","Tsubasa","Ryusei","Haru",
    "Yuma","Ryo","Kohei","Shun","Taiga","Kaoru","Jun","Satoshi","Akira","Noboru"
  ],
  female: [
    "Yui","Aoi","Yuna","Rin","Hina","Koharu","Akari","Mei","Sakura","Yuzuki",
    "Ichika","Hana","Riko","Miyu","Ema","Nanami","Kokoro","Himari","Tsumugi","Sara",
    "Yumi","Ayaka","Rina","Nao","Kanon","Momoka","Suzu","Airi","Chinatsu","Erika",
    "Kaori","Misaki","Natsuki","Reina","Shiori","Yoko","Yuki","Mio","Wakana","Hikari"
  ],
  last: [
    "Sato","Suzuki","Takahashi","Tanaka","Watanabe","Ito","Yamamoto","Nakamura","Kobayashi","Kato",
    "Yoshida","Yamada","Sasaki","Yamaguchi","Matsumoto","Inoue","Kimura","Hayashi","Shimizu","Saito",
    "Mori","Abe","Ikeda","Hashimoto","Yamashita","Ishikawa","Ogawa","Goto","Okada","Hasegawa",
    "Murakami","Kondo","Ishii","Sakamoto","Endo","Aoki","Fujita","Nishimura","Fukuda","Ota"
  ]
};

function randomJapaneseFirst(gender){
  if(gender === "male") return pick(JAPANESE_DB.male);
  if(gender === "female") return pick(JAPANESE_DB.female);
  return pick(Math.random() < 0.5 ? JAPANESE_DB.male : JAPANESE_DB.female);
}

function generateJapaneseNameList({ type = "full", gender = "both", count = 50 }){
  const out = []; const seen = new Set(); let attempts = 0;
  while(out.length < count && attempts < count * 20){
    attempts++;
    let name;
    if(type === "first"){ name = randomJapaneseFirst(gender); }
    else if(type === "last"){ name = pick(JAPANESE_DB.last); }
    else { name = `${randomJapaneseFirst(gender)} ${pick(JAPANESE_DB.last)}`; }
    const key = name.toLowerCase();
    if(seen.has(key)) continue;
    seen.add(key); out.push(name);
  }
  return out;
}

const ELF_DB = {
  male: [
    "Thalendir","Caelith","Faelar","Ithrandor","Silvaen","Aerendyl","Voranthiel","Belegorn","Nimrodel","Calenmir",
    "Erevan","Galinor","Miraval","Sylvaris","Threndil","Aldarion","Ceredhil","Duvarian","Elrendal","Fyrandor",
    "Isilmar","Lorendil","Maethriel","Naeloth","Ondariel","Peredhil","Quellith","Rivendal","Serathil","Talvorin"
  ],
  female: [
    "Aelindra","Sylvanwe","Elowyn","Faelivara","Nimriel","Ithrenya","Caladwen","Miravel","Thalassiel","Vaelira",
    "Amariel","Belorien","Celestwyn","Dornya","Elaneth","Fynwen","Ilsevel","Lunariel","Maelithra","Naevys",
    "Oriwen","Perenwyn","Quiravel","Rithwen","Selenya","Talwenna","Ulvarien","Vyrenne","Wrenithil","Ysolwen"
  ],
  last: [
    "Moonshadow","Silverleaf","Starweaver","Windwhisper","Nightbloom","Duskwalker","Dawnbringer","Frostvale","Thornwood","Silverbrook",
    "Emberfall","Mistrunner","Wyldwood","Ashgrove","Riversong","Stormrune","Suncrest","Shadowmere","Wraithwind","Glimmerfen"
  ]
};

function randomElfFirst(gender){
  if(gender === "male") return pick(ELF_DB.male);
  if(gender === "female") return pick(ELF_DB.female);
  return pick(Math.random() < 0.5 ? ELF_DB.male : ELF_DB.female);
}

function generateElfNameList({ type = "full", gender = "both", count = 50 }){
  const out = []; const seen = new Set(); let attempts = 0;
  while(out.length < count && attempts < count * 20){
    attempts++;
    let name;
    if(type === "first"){ name = randomElfFirst(gender); }
    else if(type === "last"){ name = pick(ELF_DB.last); }
    else { name = `${randomElfFirst(gender)} ${pick(ELF_DB.last)}`; }
    const key = name.toLowerCase();
    if(seen.has(key)) continue;
    seen.add(key); out.push(name);
  }
  return out;
}

const BAND_DB = {
  adjectives: [
    "Broken","Electric","Velvet","Crimson","Silent","Wild","Golden","Neon","Hollow","Restless",
    "Wandering","Radiant","Feral","Lucid","Blind","Copper","Midnight","Sonic","Static","Crooked",
    "Faded","Vivid","Reckless","Distant","Sacred","Savage","Endless","Rogue","Fractured","Rusted"
  ],
  nouns: [
    "Wolves","Ravens","Machines","Echoes","Riot","Static","Empire","Bones","Signals","Ghosts",
    "Horizon","Kingdom","Rebels","Circuit","Storm","Serpents","Vultures","Compass","Wildfire","Anthem",
    "Voyage","Cascade","Renegades","Hollows","Mirage","Fable","Halo","Static","Fever","Waves"
  ],
  singleWords: [
    "Aftershock","Paperclip","Windmill","Tangerine","Gravity","Sundial","Static","Voyager","Meridian",
    "Halcyon","Threadbare","Kaleidoscope","Afterglow","Waypoint","Lowtide","Sparrow","Nightbus","Amplitude"
  ]
};

function generateBandNameList(count = 50){
  const out = []; const seen = new Set(); let attempts = 0;
  while(out.length < count && attempts < count * 25){
    attempts++;
    const style = Math.floor(Math.random() * 4);
    let name;
    if(style === 0) name = `The ${pick(BAND_DB.adjectives)} ${pick(BAND_DB.nouns)}`;
    else if(style === 1) name = `${pick(BAND_DB.nouns)} & The ${pick(BAND_DB.adjectives)}`;
    else if(style === 2) name = pick(BAND_DB.singleWords);
    else name = `${pick(BAND_DB.adjectives)} ${pick(BAND_DB.singleWords)}`;
    if(seen.has(name)) continue;
    seen.add(name); out.push(name);
  }
  return out;
}

const CITY_DB = {
  prefixes: ["New","North","South","East","West","Port","Lake","Fort","Mount","San","Fair","Green","Silver","Oak","Stone"],
  roots: ["haven","field","brook","dale","ridge","wood","ford","view","hollow","crest","bury","mont","gate","spring","vale","meadow","glen","harbor","hurst","wick"],
  suffixes: ["ton","ville","burg","shire","port","land","holm","stead","boro","ham"],
  standalone: ["Rivermouth","Ashfall","Copperfield","Redcliff","Millbrook","Windermoor","Stonebridge","Blackwater","Ironforge","Wheatland"]
};

function generateCityNameList(count = 50){
  const out = []; const seen = new Set(); let attempts = 0;
  while(out.length < count && attempts < count * 25){
    attempts++;
    const style = Math.floor(Math.random() * 4);
    let name;
    if(style === 0) name = `${pick(CITY_DB.prefixes)} ${pick(CITY_DB.roots).replace(/^./, c => c.toUpperCase())}`;
    else if(style === 1) name = `${pick(CITY_DB.roots).replace(/^./, c => c.toUpperCase())}${pick(CITY_DB.suffixes)}`;
    else if(style === 2) name = pick(CITY_DB.standalone);
    else name = `${pick(CITY_DB.prefixes)} ${pick(CITY_DB.standalone)}`;
    if(seen.has(name)) continue;
    seen.add(name); out.push(name);
  }
  return out;
}

const SCHOOL_DB = {
  names: [
    "Lincoln","Riverside","Jefferson","Franklin","Madison","Oakwood","Maplewood","Fairview","Kennedy","Washington",
    "Hillcrest","Westbrook","Sunnyvale","Greenfield","Northgate","Cedar Ridge","Eastwood","Clearview","Brookside","Highland"
  ],
  types: {
    elementary: ["Elementary School","Primary School"],
    high: ["High School","Senior High School"],
    college: ["Academy","Preparatory Academy","Institute","College"]
  }
};

function generateSchoolNameList({ type = "high", count = 50 }){
  const out = []; const seen = new Set(); let attempts = 0;
  const pool = SCHOOL_DB.types[type] || SCHOOL_DB.types.high;
  while(out.length < count && attempts < count * 25){
    attempts++;
    const name = `${pick(SCHOOL_DB.names)} ${pick(pool)}`;
    if(seen.has(name)) continue;
    seen.add(name); out.push(name);
  }
  return out;
}
