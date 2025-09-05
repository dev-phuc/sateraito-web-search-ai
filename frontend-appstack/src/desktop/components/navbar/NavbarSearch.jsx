// Framework import
import React, { useContext, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  createSearchParams, useLocation, useNavigate, useParams, useSearchParams,
} from "react-router-dom";

// Redux components
// import { selectTypeBook } from "@/redux/slices/type_book";
// import { selectCategories } from "@/redux/slices/categories";

// Hook components
import useAppDispatch from "@/hooks/useAppDispatch";
import useAppSelector from "@/hooks/useAppSelector";
import useUserConfig from "@/hooks/useUserConfig";

// Context components

// Library imports
// Library IU imports
import {
  Button, Form, InputGroup, Card, Row, Col, OverlayTrigger, Tooltip,
} from "react-bootstrap";


const NavbarSearch = () => {
  // Use default
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const useParam = useParams();

  const inputSearchRef = useRef();
  const advanceSearchRef = useRef();

  // Constant value
  const optionSort = [
    { name: t("SORT_BY_JOINED"), value: 'total_join' },
    { name: t("SORT_BY_POPULAR"), value: 'popular' },
    { name: t("SORT_BY_CREATED_AT"), value: 'created_date' },
  ]
  const initialState = {
    show: false,
    keyword: "",
    title: "",
    // time_ago: "",
    // date: "",

    type_book_id: "",
    category_id: "",
    sort_by: "",
  };

  // Use hooks state

  // Use state
  const [searchParams, setSearchParams] = useSearchParams();
  const typeBooks = useAppSelector(state => selectTypeBook(state.type_book))
  const categories = useAppSelector(state => selectCategories(state.categories))

  const [state, setState] = useState(initialState);
  const [timeAgoSearch, setTimeAgoSearch] = useState([
    {
      value: "1_day",
      title: t("TIME_1DAY"),
    },
    {
      value: "3_day",
      title: t("TIME_3DAY"),
    },
    {
      value: "1_week",
      title: t("TIME_1WEEK"),
    },
    {
      value: "2_week",
      title: t("TIME_2WEEK"),
    },
    {
      value: "1_month",
      title: t("TIME_1MONTH"),
    },
    {
      value: "2_month",
      title: t("TIME_2MONTH"),
    },
    {
      value: "3_month",
      title: t("TIME_3MONTH"),
    },
    {
      value: "6_month",
      title: t("TIME_6MONTH"),
    },
    {
      value: "1_year",
      title: t("TIME_1YEAR"),
    },
  ]);

  useEffect(() => {
    const keyword = searchParams.get("keyword") || "";
    const title = searchParams.get("title") || "";
    // const time_ago = searchParams.get("time_ago") || "";
    // const date = searchParams.get("date") || "";

    const type_book_id = searchParams.get("type_book_id") || "";
    const category_id = searchParams.get("category_id") || "";
    const sort_by = searchParams.get("sort_by") || "";

    setState({
      ...state,
      keyword,
      title,
      // time_ago,
      // date,
      type_book_id,
      category_id,
      sort_by,
    });

  }, [searchParams]);

  function handleShowPopup() {
    setState({ ...state, show: !state.show });
  }

  function handleHidePopup() {
    setState(initialState);
  }

  function handleChange(e) {
    const { name, value } = e.target;

    if (name == 'type_book_id') {
      setState({ ...state, [name]: value, ['category_id']: '' });
    } else {
      setState({ ...state, [name]: value });
    }
  }

  function clearSearch() {
    setState({ ...initialState });
    navigate({
      pathname: "/search",
    });
  }

  const handleSubmit = async (e) => {
    handleHidePopup();
    redirectSearch();
  };

  const redirectSearch = () => {
    let object_search = {};
    if (state.keyword && state.keyword.trim() != '') {
      object_search.keyword = state.keyword;
    }
    if (state.title && state.title.trim() != '') {
      object_search.title = state.title;
    }
    // if (state.time_ago && state.time_ago.trim() != '') {
    //   object_search.time_ago = state.time_ago;
    // }
    // if (state.date && state.date.trim() != '') {
    //   object_search.date = state.date;
    // }
    if (state.type_book_id && state.type_book_id.trim() != '') {
      object_search.type_book_id = state.type_book_id;
    }
    if (state.category_id && state.category_id.trim() != '') {
      object_search.category_id = state.category_id;
    }
    if (state.sort_by && state.sort_by.trim() != '') {
      object_search.sort_by = state.sort_by;
    }

    navigate({
      pathname: "/search",
      search: `?${createSearchParams(object_search)}`,
    });
  };

  useEffect(() => {
    function handleKeypress(e) {
      console.log("Keypress event triggered", e, e.target.classList);
      if (!e.shiftKey && e.key === "Escape") {
        handleHidePopup();
      }
    }
    function handleClick(e) {
      console.log("click event triggered", e, e.target.classList);

      if (e.target.classList.contains("top-nav-button-search")) {
        return false;
      }
      if (
        e.target.classList.contains("top-nav-popup-search") ||
        e.target.closest(".top-nav-popup-search")
      ) {
        console.log("is top-nav-popup-search");
      } else {
        handleHidePopup();
      }
    }
    if (state.show) {
      document.body.addEventListener("keydown", handleKeypress);
      document.body.addEventListener("click", handleClick);
      return () => {
        document.body.removeEventListener("keydown", handleKeypress);
        document.body.removeEventListener("click", handleClick);
      };
    } else {
      document.body.removeEventListener("keydown", handleKeypress);
      document.body.removeEventListener("click", handleClick);
      return () => {
        document.body.removeEventListener("keydown", handleKeypress);
        document.body.removeEventListener("click", handleClick);
      };
    }
  }, [state.show]);

  return (
    <div inline="true"
      className={
        "d-none d-sm-inline-block header-search " +
        (state.keyword ? "show-search-quick" : "")
      }
    >
      <InputGroup className="ig-header-search">
        <Form.Control
          ref={(el) => {
            if (el) {
              inputSearchRef.current = el;
            }
          }}
          tabIndex={1}
          name="keyword"
          value={state.keyword}
          onChange={handleChange}
          onBlur={handleChange}
          onKeyDown={(event) => {
            if (!event.shiftKey && event.key === "Enter") {
              if (state.keyword) {
                redirectSearch();
              }
            }
          }}
          placeholder={t("Search")}
          type="text"
          className="header-search-input"
        />
        <Button
          className="btn-search-onchange mdi mdi-close"
          variant=""
          onClick={clearSearch}
        >
        </Button>

        <OverlayTrigger
          placement="bottom"
          delay={{ show: 250, hide: 400 }}
          overlay={<Tooltip>{t("ADVANCE_SEARCH")}</Tooltip>}
        >
          <Button
            ref={(el) => {
              if (el) {
                advanceSearchRef.current = el;
              }
            }}
            tabIndex={1}
            type="button"
            className="top-nav-button-search btn-search"
            variant=""
            onClick={handleShowPopup}
          >
            <span className="mdi mdi-tune"></span>
          </Button>
        </OverlayTrigger>
      </InputGroup>
      <div
        className={
          "top-nav-popup-search form-search " + (state.show ? "show" : "")
        }
      >
        <Card>
          <Card.Body>
            <Form>
              <Form.Group as={Row} className="mb-c-20">
                <Form.Label column sm={3} className="text-sm-right">
                  <span className="mdi mdi-text ico-lbl"></span>
                  {t("LABEL_INPUT_TITLE_BOOK")}
                </Form.Label>
                <Col sm={9}>
                  <Form.Control
                    name="title"
                    value={state.title}
                    onChange={handleChange}
                    onBlur={handleChange}
                    type="text"
                    tabIndex={1}
                  />
                </Col>
              </Form.Group>

              {/* <Form.Group as={Row} className="mb-c-20">
                <Form.Label column sm={3} className="text-sm-right">
                  <span className="mdi mdi-calendar-clock ico-lbl"></span>
                  {t("LABEL_INPUT_DAY_WITHIN")}
                </Form.Label>
                <Col md={4}>
                  <Form.Group className="mb-c-20">
                    <Form.Select
                      name="time_ago"
                      value={state.time_ago}
                      onChange={handleChange}
                      onBlur={handleChange}
                      tabIndex={1}
                    >
                      <option value="">{t("DEFAULT_ALL_OPTION")}</option>
                      {timeAgoSearch
                        ? timeAgoSearch.map((item) => {
                          return (
                            <option key={Math.random()} value={item.value}>
                              {item.title}
                            </option>
                          );
                        })
                        : ""}
                    </Form.Select>
                  </Form.Group>
                </Col>
                <Col md={5}>
                  <Form.Group className="mb-c-20">
                    <Form.Control
                      name="date"
                      type="date"
                      value={state.date}
                      onChange={handleChange}
                      tabIndex={1}
                    />
                  </Form.Group>
                </Col>
              </Form.Group> */}

              <Form.Group as={Row} className="mb-c-20">
                <Form.Label column sm={3} className="text-sm-right">
                  <span className="mdi mdi-format-list-bulleted-type ico-lbl"></span>
                  {t("LABEL_INPUT_DAY_WITHIN")}
                </Form.Label>

                <Col md={4}>
                  <Form.Select name="type_book_id"
                    value={state.type_book_id}
                    tabIndex={1}
                    onChange={handleChange}>
                    <option></option>
                    {typeBooks.map((typeBook, index) => (
                      <option key={typeBook.id} value={typeBook.id} defaultValue={state.type_book_id == typeBook.id}>{typeBook.name}</option>
                    ))}
                  </Form.Select>
                </Col>

                <Col md={5}>
                  <Form.Select name="category_id"
                    value={state.category_id}
                    tabIndex={1}
                    onChange={handleChange}
                  >
                    <option value=""></option>
                    {state.type_book_id != '' ?
                      <>
                        {categories.filter(item => item.type_parent_id == state.type_book_id).map((category, index) => (
                          <option key={index} value={category.id} defaultValue={state.category_id == category.id}>{category.name}</option>
                        ))}
                      </>
                      :
                      <>
                        {categories.map((category, index) => (
                          <option key={index} value={category.id} defaultValue={state.category_id == category.id}>{category.name}</option>
                        ))}
                      </>
                    }
                  </Form.Select>
                </Col>

              </Form.Group>

              <Form.Group as={Row} className="mb-c-20">
                <Form.Label column sm={3} className="text-sm-right">
                  <span className="mdi mdi-sort ico-lbl"></span>
                  {t("SORT_BY")}
                </Form.Label>

                <Col sm={9}>
                  <Form.Select name="sort_by"
                    value={state.sort_by}
                    tabIndex={1}
                    onChange={handleChange}
                  >
                    <option value=""></option>
                    {optionSort.map((item, index) => (
                      <option key={index} value={item.value} defaultValue={state.sort_by == item.value}>
                        {item.name}
                      </option>
                    ))}

                  </Form.Select>
                </Col>
              </Form.Group>

              <Form.Group as={Row} className="mb-c-20">
                <Col sm={{ size: 10, offset: 2 }} className="btn-submit">
                  <Button
                    className="st-btn-material-text btn"
                    variant=""
                    onClick={handleHidePopup}
                    // onKeyDown={(event) => {
                    //   if (!event.shiftKey && event.key === "Enter") {
                    //     if (state.keyword) {
                    //       handleHidePopup(event);
                    //     }
                    //   }
                    // }}
                    tabIndex={1}
                  >
                    {t("BTN_CANCEL")}
                  </Button>
                  <Button
                    variant=""
                    className="st-btn-material"
                    onClick={handleSubmit}
                    // onKeyDown={(event) => {
                    //   if (!event.shiftKey && event.key === "Enter") {
                    //     if (state.keyword) {
                    //       handleSubmit(event);
                    //     }
                    //   }
                    // }}
                    tabIndex={1}
                  >
                    <i className="mdi mdi-magnify"></i>
                    {t("BTN_SEARCH")}
                  </Button>
                </Col>
              </Form.Group>

            </Form>
          </Card.Body>
        </Card>
      </div>
    </div>
  );
};

export default NavbarSearch;
