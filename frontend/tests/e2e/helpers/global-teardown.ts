import * as fs from 'fs';
import * as path from 'path';

const authStatePath = path.join(__dirname, '..', '.auth', 'user.json');

export default async function globalTeardown() {
  if (fs.existsSync(authStatePath)) {
    fs.unlinkSync(authStatePath);
  }
}