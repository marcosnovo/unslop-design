export const A = () => (
  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)" }}>
    <div className="rounded-lg bg-white p-4"><p>42</p></div>
    <div className="rounded-lg bg-white p-4"><p>43</p></div>
    <div className="rounded-lg bg-white p-4"><p>44</p></div>
  </div>
);
export const B = () => (
  <div style={{ display: "flex", gap: 8 }}>
    <div className="rounded-md bg-gray-50 p-4"><p>1</p></div>
    <div className="rounded-md bg-gray-50 p-4"><p>2</p></div>
    <div className="rounded-md bg-gray-50 p-4"><p>3</p></div>
  </div>
);
