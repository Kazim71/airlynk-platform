const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'], defaultViewport: { width: 1280, height: 800 } });
  const page = await browser.newPage();
  
  const unique = Date.now();

  await page.goto('http://localhost:4000/register', { waitUntil: 'networkidle0' });
  
  await page.waitForSelector('input[name=full_name]');
  await page.type('input[name=full_name]', 'Puppeteer Test');
  await page.type('input[name=email]', `passenger_${unique}@example.com`);
  await page.type('input[name=password]', 'StrongPassword123!');
  await page.click('button[type=submit]');
  
  try {
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 });
  } catch(e) {}
  
  await page.goto('http://localhost:4000/booking', { waitUntil: 'networkidle0' });
  
  // Select Delhi (DEL)
  await page.waitForSelector('select');
  await page.select('select', 'DEL');
  
  await page.type('input[type=date]', '2026-10-10');
  await page.type('input[type=time]', '10:00');
  
  const buttons = await page.$$('button');
  for (const b of buttons) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text.includes('Get Premium Estimate')) {
      await b.click();
      break;
    }
  }
  
  await new Promise(r => setTimeout(r, 2000));
  
  const buttons2 = await page.$$('button');
  for (const b of buttons2) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text.includes('Confirm & Proceed')) {
      await b.click();
      break;
    }
  }
  
  await new Promise(r => setTimeout(r, 4000));
  
  const buttons3 = await page.$$('button');
  for (const b of buttons3) {
    const text = await page.evaluate(el => el.textContent, b);
    if (text.includes('Pay Now (Mock)')) {
      await b.click();
      break;
    }
  }
  
  await new Promise(r => setTimeout(r, 4000));
  
  await page.screenshot({ path: 'booking_success.png', fullPage: true });
  console.log("FINAL URL:", page.url());
  
  await browser.close();
})();
