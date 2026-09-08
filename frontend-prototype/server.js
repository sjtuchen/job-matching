const http = require('http');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const port = 4173;

const mime = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml'
};

http.createServer((request, response) => {
  const urlPath = request.url.split('?')[0];
  const filePath = path.join(root, urlPath === '/' ? 'index.html' : urlPath);
  fs.readFile(filePath, (error, data) => {
    if (error) {
      response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      response.end('Not found');
      return;
    }
    response.writeHead(200, { 'Content-Type': mime[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
    response.end(data);
  });
}).listen(port, () => {
  console.log(`Serving frontend-prototype at http://localhost:${port}`);
});
