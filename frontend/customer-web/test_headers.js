const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  
  page.on('request', request => {
    if (request.url().includes('api/v1')) {
      console.log('REQUEST URL:', request.url(), request.method());
      console.log('REQUEST HEADERS:', request.headers());
    }
  });
  
  page.on('response', response => {
    if (response.url().includes('api/v1')) {
      console.log('RESPONSE URL:', response.url(), 'STATUS:', response.status());
    }
  });

  const unique = Date.now();

  await page.goto('http://localhost:4000/register');
  
  await page.type('input[name=full_name]', 'Puppeteer Test');
  await page.type('input[name=email]', `passenger_${unique}@example.com`);
  await page.type('input[name=password]', 'StrongPassword123!');
  await page.click('button[type=submit]');
  
  try {
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 });
  } catch(e) {
    console.log("Nav timeout, current URL:", page.url());
  }
  
  await page.goto('http://localhost:4000/booking', { waitUntil: 'networkidle0' });
  
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
  console.log("FINAL URL:", page.url());
  await browser.close();
})();
