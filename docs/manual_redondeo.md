# Manual de redondeo de decimales en cotizaciones

## 1. Por qué falla el redondeo

1. **`float` no es exacto.** `2.675` se guarda como `2.67499999...`, así que `round(2.675, 2)` da `2.67`, no `2.68`.
2. **`round()` de Python usa redondeo bancario** (mitad al par): `round(0.5)=0`, `round(1.5)=2`, `round(2.5)=2`. Excel redondea la mitad hacia arriba. Esa es la causa típica de las diferencias entre Excel y Python.
3. **Redondear en distintos momentos** (por línea o al final) cambia el total por centavos.

## 2. Reglas de oro

| # | Regla |
|---|-------|
| 1 | Usar `Decimal`, nunca `float`, para dinero. Crearlo desde texto: `Decimal("2.675")`, no `Decimal(2.675)`. |
| 2 | Un solo modo de redondeo en todo el sistema: **ROUND_HALF_UP** (igual que Excel). |
| 3 | Redondear a 2 decimales solo en los puntos definidos en la sección 3. No redondear resultados intermedios. |
| 4 | El total es la **suma de los importes ya redondeados**, no el redondeo de una suma sin redondear. |
| 5 | Mostrar y guardar el mismo valor. Lo que ve el cliente en el PDF debe ser lo que está en la base de datos. |

## 3. Orden de cálculo de una cotización

Política recomendada (decídela una vez y no la cambies):

```
1. Importe de línea  = redondear(cantidad × precio unitario)
2. Descuento de línea = redondear(importe de línea × % descuento)
3. Base de línea      = importe de línea − descuento de línea
4. Subtotal           = suma de las bases de línea
5. Descuento global   = redondear(subtotal × % descuento global)   (si existe)
6. Base imponible     = subtotal − descuento global
7. Impuesto           = redondear(base imponible × tasa)
8. Total              = base imponible + impuesto
```

Se calcula el impuesto **una vez sobre la base imponible**, no línea por línea. Calcularlo por línea y sumar da diferencias de centavos frente al total. Si el cliente o el SAT exigen impuesto por línea, se usa la variante por línea, pero se aplica en todas partes igual.

## 4. Código de referencia (Python)

```python
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

def d(valor) -> Decimal:
    """Convierte a Decimal desde texto, nunca desde float."""
    return Decimal(str(valor))

def r2(valor: Decimal) -> Decimal:
    """Redondea a 2 decimales, mitad hacia arriba (como Excel)."""
    return d(valor).quantize(CENT, rounding=ROUND_HALF_UP)

def cotizar(lineas, desc_global_pct="0", iva_pct="16"):
    subtotal = Decimal("0")
    for cantidad, precio, desc_pct in lineas:
        importe = r2(d(cantidad) * d(precio))
        descuento = r2(importe * d(desc_pct) / 100)
        subtotal += importe - descuento
    desc_global = r2(subtotal * d(desc_global_pct) / 100)
    base = subtotal - desc_global
    iva = r2(base * d(iva_pct) / 100)
    return {"subtotal": subtotal, "descuento_global": desc_global,
            "base": base, "iva": iva, "total": base + iva}
```

## 5. Equivalencias con Excel

| Necesidad | Excel | Python |
|-----------|-------|--------|
| Redondear a 2 decimales | `=REDONDEAR(A1;2)` | `r2(x)` |
| Hacia arriba siempre | `=REDONDEAR.MAS(A1;2)` | `quantize(CENT, ROUND_UP)` |
| Truncar | `=TRUNCAR(A1;2)` | `quantize(CENT, ROUND_DOWN)` |
| Solo cambiar el formato | formato de celda (no cambia el valor) | no usar |

**Cuidado:** el formato de celda en Excel solo muestra 2 decimales, pero el valor interno sigue teniendo todos. Por eso las sumas en pantalla pueden no cuadrar. Envuelve con `REDONDEAR` en cada paso que corresponda según la sección 3.

## 6. Casos de prueba

| Caso | Entrada | Esperado |
|------|---------|----------|
| Mitad exacta | `r2(2.675)` | `2.68` |
| Mitad exacta (`round()` daría `0.12`) | `r2(0.125)` | `0.13` |
| Float traicionero | `r2(1.005)` | `1.01` |
| IVA | base `100.05` × 16 % | `16.01` |
| Descuento | `99.99` × 15 % | `15.00` |

## 7. Lista de verificación para revisar el código

- [ ] Buscar `round(` y `float(`: reemplazar por `r2` y `Decimal`.
- [ ] Buscar `* 1.16`, `* 0.85` y similares: usar `iva_pct` y `desc_pct` como `Decimal`.
- [ ] Confirmar que existe una sola función de redondeo y que todos la usan.
- [ ] Confirmar que Excel y Python usan el mismo orden de cálculo (sección 3).
- [ ] Comparar una cotización real en Excel y en Python hasta el centavo.
