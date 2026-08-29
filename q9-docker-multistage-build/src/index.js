const http = require('http');

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('q9 stub app is running\n');
});

server.listen(3000, () => {
  console.log('listening on port 3000');
});
