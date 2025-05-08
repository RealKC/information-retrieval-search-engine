use pyo3::{exceptions::PyValueError, prelude::*};
use robotxt::{url::Url, Robots};

const USER_AGENT: &str = "RI Web Crawler (dumitru.mitca@student.tuiasi.ro)";

#[pyclass]
struct RobotsTxt {
    inner: robotxt::Robots,
}

#[pymethods]
impl RobotsTxt {
    #[staticmethod]
    fn from_contents(robotstxt: &str) -> Self {
        Self {
            inner: Robots::from_bytes(robotstxt.as_bytes(), USER_AGENT),
        }
    }

    #[staticmethod]
    fn deserialize(serialized: &str) -> PyResult<Self> {
        match serde_json::from_str(serialized) {
            Ok(val) => Ok(Self { inner: val }),
            Err(err) => Err(PyValueError::new_err(err.to_string())),
        }
    }

    fn serialize(&self) -> PyResult<String> {
        match serde_json::to_string(&self.inner) {
            Ok(val) => Ok(val),
            Err(err) => Err(PyValueError::new_err(err.to_string())),
        }
    }

    fn is_allowed(&self, url: &str) -> bool {
        let Ok(url) = Url::parse(url) else {
            return self.inner.is_relative_allowed(url);
        };

        return self.inner.is_absolute_allowed(&url);
    }
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("USER_AGENT", USER_AGENT)?;
    m.add_class::<RobotsTxt>()?;
    Ok(())
}
