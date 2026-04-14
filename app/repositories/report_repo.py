from sqlalchemy.orm import Session
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate


def create_report(db: Session, report_data: ReportCreate) -> Report:
    """
    Create a new report in the database.

    Args:
        db (Session): SQLAlchemy database session.
        report_data (ReportCreate): Report input data.

    Returns:
        Report: The created report object.
    """
    db_report = Report(**report_data.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report(db: Session, report_id: int) -> Report | None:
    """
    Retrieve a report by report ID.

    Args:
        db (Session): SQLAlchemy database session.
        report_id (int): ID of the report.

    Returns:
        Report | None: Report object if found, otherwise None.
    """
    return db.query(Report).filter(Report.report_id == report_id).first()


def update_report(db: Session, report_id: int, report_data: ReportUpdate) -> Report | None:
    """
    Update an existing report.

    Args:
        db (Session): SQLAlchemy database session.
        report_id (int): ID of the report to update.
        report_data (ReportUpdate): Updated report data.

    Returns:
        Report | None: Updated report object if found, otherwise None.
    """
    db_report = get_report(db, report_id)
    if not db_report:
        return None

    update_data = report_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_report, field, value)

    db.commit()
    db.refresh(db_report)
    return db_report


def delete_report(db: Session, report_id: int) -> Report | None:
    """
    Delete a report from the database.

    Args:
        db (Session): SQLAlchemy database session.
        report_id (int): ID of the report to delete.

    Returns:
        Report | None: Deleted report object if found, otherwise None.
    """
    db_report = get_report(db, report_id)
    if not db_report:
        return None

    db.delete(db_report)
    db.commit()
    return db_report


def list_reports(db: Session, skip: int = 0, limit: int = 100) -> list[Report]:
    """
    Retrieve a list of reports with pagination.

    Args:
        db (Session): SQLAlchemy database session.
        skip (int): Number of records to skip.
        limit (int): Maximum number of reports to return.

    Returns:
        list[Report]: List of report objects.
    """
    return db.query(Report).offset(skip).limit(limit).all()