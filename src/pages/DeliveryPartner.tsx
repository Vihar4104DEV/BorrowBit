import { useEffect, useMemo, useState } from "react";
import { Navigation } from "@/components/Navigation";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table";
import { Dialog, DialogContent, DialogTrigger } from "@/components/ui/dialog";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { Calendar, MapPin, CheckCircle, XCircle, Clock, Map, Camera, ArrowRight } from "lucide-react";
import { ResponsiveContainer, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Bar, LineChart, Line } from "recharts";

type JobStatus =
  | "pending"
  | "accepted"
  | "on_the_way"
  | "picked_up"
  | "in_transit"
  | "delivered"
  | "returned"
  | "completed";

type JobType = "Pickup" | "Return";

type Job = {
  id: string;
  type: JobType;
  customer: string;
  address: string;
  scheduled: string;
  status: JobStatus;
  decisionWindow: number;
  location: { lat: number; lng: number };
  beforePhotos: { name: string; url: string }[];
  afterPhotos: { name: string; url: string }[];
};

const initialJobs: Job[] = [
  {
    id: "JOB-10234",
    type: "Pickup",
    customer: "John Doe",
    address: "45 Park Avenue, NY",
    scheduled: "2025-08-12 14:30",
    status: "pending",
    decisionWindow: 120,
    location: { lat: 40.765, lng: -73.971 },
    beforePhotos: [
      { name: "before-1.jpg", url: "https://via.placeholder.com/640x480?text=Before+1" },
      { name: "before-2.jpg", url: "https://via.placeholder.com/640x480?text=Before+2" },
      { name: "before-3.jpg", url: "https://via.placeholder.com/640x480?text=Before+3" },
    ],
    afterPhotos: [
      { name: "after-1.jpg", url: "https://via.placeholder.com/640x480?text=After+1" },
      { name: "after-2.jpg", url: "https://via.placeholder.com/640x480?text=After+2" },
      { name: "after-3.jpg", url: "https://via.placeholder.com/640x480?text=After+3" },
    ],
  },
  {
    id: "JOB-10235",
    type: "Return",
    customer: "Jane Smith",
    address: "12 Main St, NY",
    scheduled: "2025-08-13 10:00",
    status: "accepted",
    decisionWindow: 0,
    location: { lat: 40.712, lng: -74.006 },
    beforePhotos: [
      { name: "before-1.jpg", url: "https://via.placeholder.com/640x480?text=Before+1" },
      { name: "before-2.jpg", url: "https://via.placeholder.com/640x480?text=Before+2" },
    ],
    afterPhotos: [
      { name: "after-1.jpg", url: "https://via.placeholder.com/640x480?text=After+1" },
      { name: "after-2.jpg", url: "https://via.placeholder.com/640x480?text=After+2" },
    ],
  },
  {
    id: "JOB-10236",
    type: "Pickup",
    customer: "Michael Green",
    address: "210 Broadway, NY",
    scheduled: "2025-08-13 16:00",
    status: "in_transit",
    decisionWindow: 0,
    location: { lat: 40.713, lng: -74.0065 },
    beforePhotos: [
      { name: "before-1.jpg", url: "https://via.placeholder.com/640x480?text=Before+1" },
    ],
    afterPhotos: [
      { name: "after-1.jpg", url: "https://via.placeholder.com/640x480?text=After+1" },
    ],
  },
];

const jobTypes: readonly JobType[] = ["Pickup", "Return"] as const;
const jobStatuses: readonly JobStatus[] = [
  "pending",
  "accepted",
  "on_the_way",
  "picked_up",
  "in_transit",
  "delivered",
  "returned",
  "completed",
] as const;
const statusLabels: Record<JobStatus, string> = {
  pending: "Pending",
  accepted: "Accepted",
  on_the_way: "On the Way",
  picked_up: "Picked Up",
  in_transit: "In Transit",
  delivered: "Delivered",
  returned: "Returned",
  completed: "Completed",
};
const statusColorClass: Record<JobStatus, string> = {
  pending: "bg-warning text-warning-foreground",
  accepted: "bg-accent text-accent-foreground",
  on_the_way: "bg-primary text-primary-foreground",
  picked_up: "bg-primary text-primary-foreground",
  in_transit: "bg-primary text-primary-foreground",
  delivered: "bg-success text-success-foreground",
  returned: "bg-success text-success-foreground",
  completed: "bg-success text-success-foreground",
};
const typeColorClass: Record<JobType, string> = {
  Pickup: "bg-success text-success-foreground",
  Return: "bg-primary text-primary-foreground",
};

const kpiFromJobs = (jobs: Job[]) => {
  const total = jobs.length;
  const byStatus = jobs.reduce<Record<string, number>>((acc, j) => {
    acc[j.status] = (acc[j.status] || 0) + 1;
    return acc;
  }, {});
  return {
    total,
    pending: byStatus["pending"] || 0,
    inProgress: (byStatus["accepted"] || 0) + (byStatus["on_the_way"] || 0) + (byStatus["picked_up"] || 0) + (byStatus["in_transit"] || 0),
    delivered: (byStatus["delivered"] || 0) + (byStatus["returned"] || 0) + (byStatus["completed"] || 0),
    canceled: 0,
  };
};

const trendData = [
  { date: "Mon", delivered: 10, pending: 2 },
  { date: "Tue", delivered: 12, pending: 1 },
  { date: "Wed", delivered: 15, pending: 0 },
  { date: "Thu", delivered: 9, pending: 3 },
  { date: "Fri", delivered: 14, pending: 2 },
  { date: "Sat", delivered: 13, pending: 1 },
  { date: "Sun", delivered: 16, pending: 1 },
];

const getMapUrl = (address: string) => `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
const getMapEmbedUrl = (address: string) => `https://www.google.com/maps?q=${encodeURIComponent(address)}&output=embed`;

const DeliveryPartner = () => {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [filters, setFilters] = useState({ type: "", status: "", date: "", search: "" });
  const [page, setPage] = useState(1);
  const [activeTab, setActiveTab] = useState("jobs");
  const [rejectId, setRejectId] = useState<string | null>(null);

  // countdown for pending jobs
  useEffect(() => {
    const id = setInterval(() => {
      setJobs(prev => prev.map(j => (j.status === "pending" && j.decisionWindow > 0 ? { ...j, decisionWindow: j.decisionWindow - 1 } : j)));
    }, 1000);
    return () => clearInterval(id);
  }, []);

  const kpis = useMemo(() => kpiFromJobs(jobs), [jobs]);

  // filtering/search/pagination
  const filtered = jobs.filter((j: Job) => {
    const matchesType = !filters.type || j.type === filters.type;
    const matchesStatus = !filters.status || j.status === (filters.status as JobStatus);
    const matchesDate = !filters.date || j.scheduled.startsWith(filters.date);
    const s = filters.search.toLowerCase();
    const matchesSearch = !s || j.id.toLowerCase().includes(s) || j.customer.toLowerCase().includes(s) || j.address.toLowerCase().includes(s);
    return matchesType && matchesStatus && matchesDate && matchesSearch;
  });
  const perPage = 10;
  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  const pageItems = filtered.slice((page - 1) * perPage, page * perPage);

  // status flow
  const nextStatus: Record<JobStatus, JobStatus | null> = {
    pending: "accepted",
    accepted: "on_the_way",
    on_the_way: "picked_up",
    picked_up: "in_transit",
    in_transit: "delivered",
    delivered: "completed",
    returned: "completed",
    completed: null,
  };

  const acceptJob = (id: string) => setJobs((prev: Job[]) => prev.map((j: Job) => (j.id === id ? { ...j, status: "accepted" as JobStatus, decisionWindow: 0 } : j)));
  const promptReject = (id: string) => setRejectId(id);
  const confirmReject = () => {
    if (!rejectId) return;
    setJobs((prev: Job[]) => prev.filter((j: Job) => j.id !== rejectId));
    setRejectId(null);
  };
  const cancelReject = () => setRejectId(null);

  const advanceStatus = (id: string) =>
    setJobs((prev: Job[]) =>
      prev.map((j: Job) => (j.id === id && nextStatus[j.status] ? { ...j, status: nextStatus[j.status] as JobStatus } : j))
    );

  const uploadPhotos = (id: string, stage: "before" | "after", files: FileList | null) => {
    if (!files) return;
    setJobs((prev: Job[]) =>
      prev.map((j: Job) => {
        if (j.id !== id) return j;
        const list = Array.from(files).map(f => ({ name: f.name, url: URL.createObjectURL(f) }));
        return stage === "before" ? { ...j, beforePhotos: [...j.beforePhotos, ...list] } : { ...j, afterPhotos: [...j.afterPhotos, ...list] };
      })
    );
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Delivery Partner Dashboard</h1>
            <p className="text-muted-foreground">Manage assignments, status, navigation, and condition reports.</p>
          </div>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4 mb-8">
          <Card className="shadow-card"><CardContent className="p-5"><div className="text-sm text-muted-foreground">Total</div><div className="text-2xl font-bold">{kpis.total}</div></CardContent></Card>
          <Card className="shadow-card"><CardContent className="p-5"><div className="text-sm text-muted-foreground">Pending</div><div className="text-2xl font-bold text-warning">{kpis.pending}</div></CardContent></Card>
          <Card className="shadow-card"><CardContent className="p-5"><div className="text-sm text-muted-foreground">In Progress</div><div className="text-2xl font-bold text-accent">{kpis.inProgress}</div></CardContent></Card>
          <Card className="shadow-card"><CardContent className="p-5"><div className="text-sm text-muted-foreground">Delivered/Returned</div><div className="text-2xl font-bold text-success">{kpis.delivered}</div></CardContent></Card>
          <Card className="shadow-card"><CardContent className="p-5"><div className="text-sm text-muted-foreground">Canceled</div><div className="text-2xl font-bold">{kpis.canceled}</div></CardContent></Card>
        </div>

        {/* Trends */}
        <Card className="shadow-card mb-8">
          <CardHeader><CardTitle>Weekly Delivery Trends</CardTitle></CardHeader>
          <CardContent>
            <div className="w-full h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="delivered" stroke="#22c55e" name="Delivered" />
                  <Line type="monotone" dataKey="pending" stroke="#fbbf24" name="Pending" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Feature Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-2">
          <ScrollArea>
            <div className="flex justify-center">
              <TabsList className="mb-3 gap-1 bg-transparent">
                <TabsTrigger value="jobs" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-full data-[state=active]:shadow-none">Job Dashboard</TabsTrigger>
                <TabsTrigger value="accept" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-full data-[state=active]:shadow-none">Accept/Reject</TabsTrigger>
                <TabsTrigger value="status" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-full data-[state=active]:shadow-none">Update Status</TabsTrigger>
                <TabsTrigger value="nav" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-full data-[state=active]:shadow-none">Navigation</TabsTrigger>
                <TabsTrigger value="report" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground rounded-full data-[state=active]:shadow-none">Condition Report</TabsTrigger>
              </TabsList>
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>

          {/* Job Dashboard */}
          <TabsContent value="jobs" className="h-[520px] md:h-[640px] overflow-auto">
            <Card className="shadow-card">
              <CardHeader><CardTitle>Assigned Jobs</CardTitle></CardHeader>
              <CardContent>
                {/* Filters */}
                <div className="flex flex-wrap gap-4 mb-4 items-end">
                  <div>
                    <label className="block text-xs font-medium mb-1">Job Type</label>
                    <select className="border rounded px-2 py-1 bg-background" value={filters.type} onChange={e => setFilters(f => ({ ...f, type: e.target.value }))}>
                      <option value="">All</option>
                      {jobTypes.map(t => (<option key={t} value={t}>{t}</option>))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1">Status</label>
                    <select className="border rounded px-2 py-1 bg-background" value={filters.status} onChange={e => setFilters(f => ({ ...f, status: e.target.value }))}>
                      <option value="">All</option>
                      {jobStatuses.map(s => (<option key={s} value={s}>{statusLabels[s]}</option>))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium mb-1">Date</label>
                    <input type="date" className="border rounded px-2 py-1 bg-background" value={filters.date} onChange={e => setFilters(f => ({ ...f, date: e.target.value }))} />
                  </div>
                  <div className="flex-1 min-w-[200px]">
                    <label className="block text-xs font-medium mb-1">Search</label>
                    <input type="text" className="border rounded px-2 py-1 w-full bg-background" placeholder="Job ID, customer, address..." value={filters.search} onChange={e => setFilters(f => ({ ...f, search: e.target.value }))} />
                  </div>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted">
                      <TableHead>Job ID</TableHead>
                      <TableHead>Job Type</TableHead>
                      <TableHead>Customer</TableHead>
                      <TableHead>Address</TableHead>
                      <TableHead>Scheduled Time</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pageItems.map((job) => (
                      <TableRow key={job.id}>
                        <TableCell className="font-mono font-medium">{job.id}</TableCell>
                        <TableCell><span className={`px-2 py-1 rounded text-xs font-bold ${typeColorClass[job.type]}`}>{job.type}</span></TableCell>
                        <TableCell>{job.customer}</TableCell>
                        <TableCell>
                          <a href={getMapUrl(job.address)} target="_blank" rel="noopener noreferrer" className="text-primary underline">{job.address}</a>
                        </TableCell>
                        <TableCell>{job.scheduled}</TableCell>
                        <TableCell>
                          <span className={`px-2 py-1 rounded text-xs font-bold ${statusColorClass[job.status]}`}>{statusLabels[job.status]}</span>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>

                {/* Pagination */}
                <div className="flex justify-between items-center mt-4">
                  <span className="text-xs text-muted-foreground">Page {page} of {totalPages}</span>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Prev</Button>
                    <Button variant="outline" size="sm" disabled={page === totalPages} onClick={() => setPage(p => Math.min(totalPages, p + 1))}>Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Accept/Reject */}
          <TabsContent value="accept" className="h-[520px] md:h-[640px] overflow-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.filter(j => j.status === "pending").map(job => (
                <Card key={job.id} className="shadow-card">
                  <CardHeader><CardTitle>{job.type} – {job.customer}</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground mb-1">Job ID: <span className="font-mono text-foreground">{job.id}</span></div>
                    <div className="text-sm mb-1">Address: <a href={getMapUrl(job.address)} className="text-primary underline" target="_blank" rel="noreferrer">{job.address}</a></div>
                    <div className="text-sm mb-1 flex items-center"><Calendar className="w-4 h-4 mr-1" /> {job.scheduled}</div>
                    <div className="text-sm mb-3 flex items-center"><Clock className="w-4 h-4 mr-1" /> Decision window: <span className="ml-1 font-semibold text-warning">{job.decisionWindow}s</span></div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="success" onClick={() => acceptJob(job.id)} disabled={job.decisionWindow === 0}><CheckCircle className="w-4 h-4" /> Accept</Button>
                      <Button size="sm" variant="destructive" onClick={() => promptReject(job.id)} disabled={job.decisionWindow === 0}><XCircle className="w-4 h-4" /> Reject</Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
              {jobs.filter(j => j.status === "pending").length === 0 && (
                <div className="text-muted-foreground">No new jobs to accept or reject.</div>
              )}
            </div>

            {rejectId && (
              <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
                <div className="bg-background rounded-lg shadow-elegant p-6 max-w-sm w-full">
                  <h3 className="text-lg font-semibold mb-2">Reject Job</h3>
                  <p className="text-muted-foreground mb-4">Are you sure you want to reject this job? It will be removed from your queue.</p>
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" onClick={cancelReject}>Cancel</Button>
                    <Button variant="destructive" onClick={confirmReject}>Reject</Button>
                  </div>
                </div>
              </div>
            )}
          </TabsContent>

          {/* Update Status */}
          <TabsContent value="status" className="h-[520px] md:h-[640px] overflow-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.filter(j => j.status !== "completed").map(job => (
                <Card key={job.id} className="shadow-card">
                  <CardHeader><CardTitle>{job.type} – {job.customer}</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground mb-1">Job ID: <span className="font-mono text-foreground">{job.id}</span></div>
                    <div className="text-sm mb-1">Current Status: <span className={`px-2 py-1 rounded text-xs font-bold ${statusColorClass[job.status]}`}>{statusLabels[job.status]}</span></div>
                    <div className="text-sm mb-3 flex items-center"><Calendar className="w-4 h-4 mr-1" /> {job.scheduled}</div>
                    {nextStatus[job.status] && (
                      <Button size="sm" variant="default" onClick={() => advanceStatus(job.id)}>
                        Mark as {statusLabels[nextStatus[job.status] as string]}
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    )}
                  </CardContent>
                </Card>
              ))}
              {jobs.filter(j => j.status !== "completed").length === 0 && (
                <div className="text-muted-foreground">No active jobs to update.</div>
              )}
            </div>
          </TabsContent>

          {/* Navigation Support */}
          <TabsContent value="nav" className="h-[520px] md:h-[640px] overflow-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map(job => (
                <Card key={job.id} className="shadow-card">
                  <CardHeader><CardTitle>{job.type} – {job.customer}</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-sm mb-1">Address: <span className="text-foreground">{job.address}</span></div>
                    <div className="text-sm mb-3 flex items-center"><Calendar className="w-4 h-4 mr-1" /> {job.scheduled}</div>
                    <div className="w-full h-40 rounded overflow-hidden border border-border mb-3">
                      <iframe
                        src={getMapEmbedUrl(job.address)}
                        width="100%"
                        height="100%"
                        style={{ border: 0 }}
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                      />
                    </div>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm">
                          <Map className="w-4 h-4 mr-1" /> Navigate
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-4xl">
                        <div className="w-full aspect-video">
                          <iframe
                            src={getMapEmbedUrl(job.address)}
                            width="100%"
                            height="100%"
                            style={{ border: 0 }}
                            loading="lazy"
                            referrerPolicy="no-referrer-when-downgrade"
                          />
                        </div>
                      </DialogContent>
                    </Dialog>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Condition Report */}
          <TabsContent value="report" className="h-[520px] md:h-[640px] overflow-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jobs.map(job => (
                <Card key={job.id} className="shadow-card">
                  <CardHeader><CardTitle>{job.type} – {job.customer}</CardTitle></CardHeader>
                  <CardContent>
                    <div className="text-sm text-muted-foreground mb-2">Job ID: <span className="font-mono text-foreground">{job.id}</span></div>
                    <div className="text-sm font-semibold">Before Pickup</div>
                    <div className="mt-2 grid grid-cols-3 gap-2">
                      {job.beforePhotos.map((p, idx) => (
                        <Dialog key={idx}>
                          <DialogTrigger asChild>
                            <button className="group w-full aspect-square rounded-lg border border-border overflow-hidden bg-card hover:shadow-elegant transition-smooth">
                              <img src={p.url} alt={p.name} className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform" />
                            </button>
                          </DialogTrigger>
                          <DialogContent className="max-w-3xl">
                            <img src={p.url} alt={p.name} className="w-full h-auto rounded" />
                          </DialogContent>
                        </Dialog>
                      ))}
                    </div>
                    <div className="text-sm font-semibold mt-4">After Return</div>
                    <div className="mt-2 grid grid-cols-3 gap-2">
                      {job.afterPhotos.map((p, idx) => (
                        <Dialog key={idx}>
                          <DialogTrigger asChild>
                            <button className="group w-full aspect-square rounded-lg border border-border overflow-hidden bg-card hover:shadow-elegant transition-smooth">
                              <img src={p.url} alt={p.name} className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform" />
                            </button>
                          </DialogTrigger>
                          <DialogContent className="max-w-3xl">
                            <img src={p.url} alt={p.name} className="w-full h-auto rounded" />
                          </DialogContent>
                        </Dialog>
                      ))}
                    </div>
                    {/* <div className="text-sm font-semibold mt-4">Comparison</div> */}
                    <div className="mt-2 grid grid-cols-2 gap-3">
                      {/* <div className="rounded-lg border border-border overflow-hidden bg-card">
                        {job.beforePhotos[0] && (
                          <img src={job.beforePhotos[0].url} className="w-full h-40 object-cover" />
                        )}
                        <div className="p-2 text-xs text-muted-foreground">Before</div>
                      </div>
                      <div className="rounded-lg border border-border overflow-hidden bg-card">
                        {job.afterPhotos[0] && (
                          <img src={job.afterPhotos[0].url} className="w-full h-40 object-cover" />
                        )}
                        <div className="p-2 text-xs text-muted-foreground">After</div>
                      </div> */}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default DeliveryPartner;
