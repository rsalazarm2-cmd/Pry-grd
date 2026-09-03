# 🦀 03. INTEGRACIÓN DEL MOTOR DE RUST (PyO3 / MATURIN)
### Extensión de Ultra-Rendimiento para Algoritmos Forenses Intensivos en CPU
**Proyecto de Maestría en Analítica de Datos | Stack: Rust 1.80+, PyO3, Maturin, Apache Arrow C Data Interface**

---

## 📌 1. JUSTIFICACIÓN ARQUITECTÓNICA DE RUST

Aunque DuckDB es el motor supremo para agregaciones relacionales SQL, existen **algoritmos forenses complejos no relacionales que no pueden expresarse eficientemente en SQL puro** o cuya ejecución en bucles nativos de Python es frenada por el **GIL (Global Interpreter Lock)**.

Para esos casos de alta complejidad matemática, la arquitectura incorpora un **Módulo de Ultra-Rendimiento en Rust**, compilado como una extensión nativa C-FFI para Python mediante **PyO3 y maturin**.

---

## ⚡ 2. INTERCAMBIO DE MEMORIA ZERO-COPY (APACHE ARROW C DATA INTERFACE)

Uno de los mayores cuellos de botella al conectar Python con extensiones C/C++/Rust es el costo de serializar y copiar grandes arreglos de datos en memoria RAM.

Nuestra arquitectura utiliza la **Apache Arrow C Data Interface**:
- **Zero-Copy Memory Access:** DuckDB exporta el resultado de la consulta SQL directamente en punteros de memoria Apache Arrow (`FFI_ArrowArray` y `FFI_ArrowSchema`).
- **Punteros Directos en RAM:** El módulo de Rust recibe los punteros de memoria RAM y ejecuta los cálculos estadísticos directamente sobre los buffers continuos sin copiar un solo byte.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ DuckDB (Memoria RAM C++) -> Genera Buffer de Vectores Apache Arrow               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Apache Arrow C Data Interface -> Punteros Directos (FFI_ArrowArray)            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Rust Extension (PyO3) -> Procesa con hilos nativos 'rayon' (100% CPU, SIN GIL)  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 3. CASOS DE USO ASIGNADOS AL MOTOR DE RUST

### 1. Test Forense de Ley de Benford (MAD - Mean Absolute Deviation)
Cómputo en paralelo sobre millones de montos para extraer el primer dígito y evaluar la desviación frente a la distribución logarítmica de Benford $P(d) = \log_{10}(1 + \frac{1}{d})$:
$$\text{MAD} = \frac{1}{9} \sum_{d=1}^9 | P_{\text{observado}}(d) - P_{\text{Benford}}(d) |$$

### 2. Entropía de Información de Shannon ($H(X)$) sobre Glosas
Evaluación de la entropía del texto en descripciones para detectar texto aleatorio, descripciones vacías repetitivas o cifrado no autorizado:
$$H(X) = -\sum_{i=1}^n P(x_i) \log_2 P(x_i)$$

### 3. Algoritmo de Grafos de Segregación de Funciones (SoD Maker-Checker)
Búsqueda de ciclos de colusión y relaciones directas entre `USUARIO_REGISTRADOR` y `USUARIO_APROBADOR` construyendo un grafo en memoria RAM Rust.

### 4. Detector de Smurfing (Splitting de Asientos)
Algoritmo de ventana deslizante temporal para identificar fragmentación de montos de $9,999 creados el mismo día para evadir el umbral de aprobación de $10,000.

---

## 💻 4. ESPECIFICACIÓN DE CÓDIGO Y ESTRUCTURA DEL MÓDULO RUST

```rust
// Extensión Rust PyO3 (src/lib.rs)
use pyo3::prelude::*;
use rayon::prelude::*;

#[pyfunction]
fn calculate_shannon_entropy_batch(texts: Vec<String>) -> PyResult<Vec<f64>> {
    // Ejecución multihilo paralela usando 'rayon' sin GIL de Python
    let results: Vec<f64> = texts
        .into_par_iter()
        .map(|text| calculate_single_entropy(&text))
        .collect();
    Ok(results)
}

fn calculate_single_entropy(text: &str) -> f64 {
    if text.is_empty() { return 0.0; }
    let mut counts = std::collections::HashMap::new();
    for ch in text.chars() {
        *counts.entry(ch).or_insert(0) += 1;
    }
    let len = text.chars().count() as f64;
    counts.values().fold(0.0, |acc, &count| {
        let p = count as f64 / len;
        acc - p * p.log2()
    })
}

#[pymodule]
fn forensic_rust_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(calculate_shannon_entropy_batch, m)?)?;
    Ok(())
}
```
