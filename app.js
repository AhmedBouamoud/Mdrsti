let all=[];
async function load(){try{let r=await fetch('assets/data/resources.json'); all=await r.json(); render(all); stats();}catch(e){document.getElementById('resources').innerHTML='<p>لم يتم تحميل الموارد بعد.</p>'}}
function render(list){document.getElementById('resources').innerHTML=list.map(x=>`<article class="card"><img src="${x.image}" onerror="this.style.display='none'"><div><span>${x.level} • ${x.type}</span><h3>${x.title}</h3><p>${x.description||''}</p><a href="${x.link}">فتح المورد</a></div></article>`).join('')}
function filterResources(cat){render(cat==='all'?all:all.filter(x=>x.level===cat||x.type===cat))}
function stats(){document.getElementById('count-all').textContent=all.length;document.getElementById('count-bac1').textContent=all.filter(x=>x.level==='الأولى باك').length;document.getElementById('count-3ac').textContent=all.filter(x=>x.level==='الثالثة إعدادي').length;document.getElementById('count-exam').textContent=all.filter(x=>x.type==='تمارين وامتحانات').length}
load();
