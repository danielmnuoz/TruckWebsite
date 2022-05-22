from django.urls import path

from . import views

urlpatterns = [
    path("user/", views.user, name="user"),
    path("admin/", views.admin, name="admin"),
    path("sponsor/", views.sponsor, name="sponsor"),
    path("selectSponsor/", views.sponsorfind, name="selectSponsor"),
    path("viewApps/", views.viewApplications, name="viewApplications"),
    path("accountInfo/", views.accountInfo, name="accountInfo"),
    path("viewSponsor", views.viewSponsor, name="viewSponsor"),
    path("viewDrivers/", views.viewDrivers, name="viewDrivers"),
    path("catalog/", views.catalog, name="catalog"),
    path("buildCatalog/", views.buildCatalog, name="buildCatalog"),
    path("orders/", views.orders, name="orders"),
    path("history/", views.history, name="history"),
    path("removeOrgs/", views.removeOrgs, name="removeOrgs"),
    path("addOrg/", views.addOrg, name="addOrg"),
    path("auditLog/", views.auditLog, name="auditLog"),
    path("error/", views.error, name="error"),

    # utility Urls
    path("acceptApp/", views.acceptApp, name="acceptApp"),
    path("denyApp/", views.denyApp, name="denyApp"),
    path("updatePoints/", views.updatePoints, name="updatePoints"),
    path("adminDelete/", views.adminDelete, name="adminDelete"),
    path("updateEmail/", views.updateEmail, name="updateEmail"),
    path("updatePassword/", views.updatePassword, name="updatePassword"),
    path("removeAccount/", views.removeAccount, name="removeAccount"),
    path("updateEmail2/", views.updateEmail2, name="updateEmail2"),
    path("updatePassword2/", views.updatePassword2, name="updatePassword2"),
    path("sponsorSales/", views.sponsorSales, name="sponsorSales"),
    path("sponsorInvoice/", views.sponsorInvoice, name="sponsorInvoice"),
    path("driverReportAll/", views.driverReportAll, name="driverReportAll"),
    path("driverReportSponsor/", views.driverReportSponsor, name="driverReportSponsor"),
    path("pointsRatio/", views.pointsRatio, name="pointsRatio"),
]
