/* Names Unlimited — name database
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
