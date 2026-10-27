const fs=require('fs');const path=require('path');
const sharp=require('C:/Users/jiaga/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
(async()=>{const root=__dirname;const names=process.argv.length>2 ? process.argv.slice(2) : fs.readdirSync(path.join(root,'svg')).filter(x=>x.endsWith('.svg'));
for(const name of names){await sharp(path.join(root,'svg',name),{density:144}).resize(1800).flatten({background:'#fff'}).png().toFile(path.join(root,'assets',name.replace('.svg','.png')));}
console.log(JSON.stringify({rasterized_native_vectors:names.length}));})().catch(e=>{console.error(e);process.exit(1)});
