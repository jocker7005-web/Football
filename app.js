// Telegram WebApp obyektini faollashtirish
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand(); // Mini App ochilganda ekranni to'liq yopishi uchun

// Telegramdan foydalanuvchi ma'lumotlarini o'qish
let userPoints = 0;
if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
    const user = tg.initDataUnsafe.user;
    document.getElementById('user-display').innerText = "Salom, " + (user.first_name || "Geymer") + "!";
}

// ADSGRAM REKLAMA SOZLAMASI
// DIQQAT: Adsgram arizangizni tasdiqlaganidan keyin beradigan raqamli ID'ni shu yerga yozasiz.
// Hozircha tizim sinov (test) rejimida ishlashi uchun "3845" (namuna ID) qoldiramiz.
const adBlockId = "3845"; 
const AdController = window.Adsgram.init({ blockId: adBlockId });

// Reklama ko'rsatish funksiyasi
function startRewardAd() {
    tg.MainButton.setText("Reklama yuklanmoqda...").show();
    
    AdController.show().then((result) => {
        // Foydalanuvchi reklamani oxirigacha ko'rsa ishlaydi
        userPoints += 150; // Har bir reklama uchun 150 ball
        document.getElementById('user-points').innerText = userPoints;
        tg.MainButton.hide();
        tg.showAlert("Ajoyib! Balansingizga 150 ball qo'shildi. Reklama sizga pul ishlash imkonini berdi!");
    }).catch((result) => {
        // Reklama yopib qo'yilganda yoki xatolikda ishlaydi
        tg.MainButton.hide();
        tg.showAlert("Bonus olish uchun reklamani oxirigacha ko'rishingiz kerak.");
    });
}

function openShop() {
    tg.showAlert("Coin & Point do'koni tez kunda to'liq ishga tushadi!");
}

function openProfile() {
    if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
        tg.showAlert("Sizning Telegram ID: " + tg.initDataUnsafe.user.id);
    } else {
        tg.showAlert("Faqat Telegram ichida ko'rish mumkin.");
    }
}
