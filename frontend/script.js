let places = [];
const grid=document.getElementById("placeGrid"), search=document.getElementById("searchInput"), count=document.getElementById("resultCount"), empty=document.getElementById("emptyState");
let activeFilter="All", selected=null, saved=[];
const photo=(url)=>url;
async function loadPlaces(){
 try{
   const response=await fetch("/api/places");
   if(!response.ok) throw new Error("Could not load destinations");
   places=await response.json();
   const fav=await fetch("/api/favorites");
   if(fav.ok) saved=(await fav.json()).map(x=>x.place_id);
   const select=document.getElementById("chosenPlace");
   select.innerHTML='<option value="">Choose a destination</option>';
   places.forEach(p=>{const o=document.createElement("option");o.value=p.id;o.textContent=`${p.name} — ${p.city}`;select.appendChild(o)});
   render();
 }catch(error){count.textContent="Unable to load places";empty.hidden=false;empty.textContent="Please start the Flask server and refresh this page."}
}
function render(){
 const q=search.value.trim().toLowerCase();
 const list=places.filter(p=>(activeFilter==="All"||p.type===activeFilter)&&[p.name,p.city,p.state,p.type,p.faith].join(" ").toLowerCase().includes(q));
 count.textContent=`${list.length} ${list.length===1?"place":"places"} to discover`;
 grid.innerHTML=list.map((p)=>`<article class="place-card" data-id="${p.id}" tabindex="0" role="button" aria-label="View ${p.name}"><div class="card-image"><img loading="lazy" src="${p.image}" alt="${p.name}" onerror="this.onerror=null;this.src='/static/images/tirumala-venkateswara-temple.svg'"><span class="card-type">${p.type}</span><span class="card-number">${String(p.id).padStart(2,"0")}</span></div><div class="card-info"><h3>${p.name}</h3><p>${p.city}, ${p.state}</p><div class="card-bottom"><span>DISCOVER PLACE</span><span>↗</span></div></div></article>`).join("");
 empty.hidden=list.length!==0;
}
function openPlace(id){
 selected=id;const p=places.find(x=>x.id===id);if(!p)return;
 document.getElementById("modalImage").src=p.image;document.getElementById("modalImage").onerror=()=>{document.getElementById("modalImage").src="/static/images/tirumala-venkateswara-temple.svg"};document.getElementById("modalImage").alt=p.name;
 document.getElementById("modalCategory").textContent=p.type;document.getElementById("modalTitle").textContent=p.name;
 document.getElementById("modalLocation").textContent=`⌖ ${p.city}, ${p.state}`;
 document.getElementById("modalDescription").textContent=p.description;
 document.getElementById("modalFaith").textContent=p.faith;document.getElementById("modalState").textContent=p.state;
 document.getElementById("mapLink").href=`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(p.name+" "+p.city)}`;
 updateSave();const m=document.getElementById("placeModal");m.classList.add("open");m.setAttribute("aria-hidden","false");document.body.style.overflow="hidden";
}
function closeModal(){const m=document.getElementById("placeModal");m.classList.remove("open");m.setAttribute("aria-hidden","true");document.body.style.overflow=""}
function updateSave(){const b=document.getElementById("savePlace"),isSaved=saved.includes(selected);b.textContent=isSaved?"✓ Saved to favourites":"♡ Save this place";b.classList.toggle("saved",isSaved)}
grid.addEventListener("click",e=>{const c=e.target.closest(".place-card");if(c)openPlace(Number(c.dataset.id))});
grid.addEventListener("keydown",e=>{if((e.key==="Enter"||e.key===" ")&&e.target.classList.contains("place-card")){e.preventDefault();openPlace(Number(e.target.dataset.id))}});
search.addEventListener("input",render);
document.getElementById("filters").addEventListener("click",e=>{const b=e.target.closest(".filter");if(!b)return;activeFilter=b.dataset.filter;document.querySelectorAll(".filter").forEach(x=>x.classList.toggle("active",x===b));render()});
document.getElementById("modalClose").onclick=closeModal;document.getElementById("modalBackdrop").onclick=closeModal;document.addEventListener("keydown",e=>{if(e.key==="Escape")closeModal()});
document.getElementById("savePlace").onclick=async()=>{
 const response=await fetch("/api/favorites",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({place_id:selected})});
 if(response.ok){const data=await response.json();if(data.saved)saved.push(selected);else saved=saved.filter(x=>x!==selected);updateSave()}
};
document.getElementById("visitForm").addEventListener("submit",async e=>{
 e.preventDefault();const payload={name:document.getElementById("visitorName").value.trim(),place_id:Number(document.getElementById("chosenPlace").value),note:document.getElementById("visitNote").value.trim()};
 const msg=document.getElementById("formMessage");
 try{const r=await fetch("/api/visits",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});const data=await r.json();if(!r.ok)throw new Error(data.error||"Could not save");msg.textContent="Your visit idea has been saved successfully! ✨";e.target.reset()}
 catch(err){msg.textContent=err.message}
});
document.getElementById("menuToggle").onclick=()=>document.getElementById("mainNav").classList.toggle("open");
document.querySelectorAll("#mainNav a").forEach(a=>a.addEventListener("click",()=>document.getElementById("mainNav").classList.remove("open")));
loadPlaces();
