import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import {
  AlertCircle,
  CheckCircle,
  XCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  Server,
  Database,
  Cloud,
  RefreshCw
} from 'lucide-react';
import { useApiKey } from '@/hooks/useApiKey';

interface SLAStatus {
  timestamp: string;
  slos: Record<string, {
    name: string;
    description: string;
    target: number;
    compliance_rate: number;
    is_met: boolean;
    indicator_count: number;
  }>;
  error_budgets: Record<string, {
    total_minutes: number;
    consumed_minutes: number;
    remaining_minutes: number;
    consumption_rate: number;
    burn_rate: number;
  }>;
  alerts: Array<{
    slo: string;
    severity: string;
    message: string;
    timestamp: string;
  }>;
}

interface RealtimeMetrics {
  api_availability: number;
  api_latency_p95: number;
  api_latency_p99: number;
  error_rate: number;
  content_success_rate: number;
  active_alerts: number;
  health_score: number;
  timestamp: string;
}

interface ServiceDependency {
  status: string;
  latency: number;
  last_check: string;
}

const SLADashboard: React.FC = () => {
  const { apiKey } = useApiKey();
  const [slaStatus, setSlaStatus] = useState<SLAStatus | null>(null);
  const [realtimeMetrics, setRealtimeMetrics] = useState<RealtimeMetrics | null>(null);
  const [dependencies, setDependencies] = useState<Record<string, ServiceDependency>>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedSLO, setSelectedSLO] = useState<string | null>(null);

  const fetchSLAData = async () => {
    if (!apiKey) return;

    try {
      setRefreshing(true);
      
      // Fetch SLA status
      const statusResponse = await fetch('/api/sla/status', {
        headers: { 'X-API-Key': apiKey }
      });
      if (statusResponse.ok) {
        setSlaStatus(await statusResponse.json());
      }

      // Fetch realtime metrics
      const metricsResponse = await fetch('/api/sla/metrics/realtime', {
        headers: { 'X-API-Key': apiKey }
      });
      if (metricsResponse.ok) {
        setRealtimeMetrics(await metricsResponse.json());
      }

      // Fetch dependencies
      const depsResponse = await fetch('/api/sla/dependencies', {
        headers: { 'X-API-Key': apiKey }
      });
      if (depsResponse.ok) {
        const depsData = await depsResponse.json();
        setDependencies(depsData.dependencies);
      }
    } catch (error) {
      console.error('Error fetching SLA data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSLAData();
    const interval = setInterval(fetchSLAData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [apiKey]);

  const getStatusColor = (isHealthy: boolean) => isHealthy ? 'text-green-600' : 'text-red-600';
  const getStatusIcon = (isHealthy: boolean) => isHealthy ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />;
  
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'error': return 'bg-orange-100 text-orange-800';
      case 'warning': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getBurnRateColor = (burnRate: number) => {
    if (burnRate >= 10) return 'text-red-600';
    if (burnRate >= 5) return 'text-orange-600';
    if (burnRate >= 2) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">SLA Dashboard</h1>
          <p className="text-gray-600 mt-1">Monitor service level agreements and objectives</p>
        </div>
        <Button
          onClick={fetchSLAData}
          disabled={refreshing}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Health Score Card */}
      {realtimeMetrics && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Overall Health Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div className="text-4xl font-bold">
                {realtimeMetrics.health_score.toFixed(1)}%
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Active Alerts</p>
                <p className="text-2xl font-semibold">{realtimeMetrics.active_alerts}</p>
              </div>
            </div>
            <Progress value={realtimeMetrics.health_score} className="mt-4" />
          </CardContent>
        </Card>
      )}

      {/* Key Metrics Grid */}
      {realtimeMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">API Availability</p>
                  <p className="text-2xl font-bold">{realtimeMetrics.api_availability.toFixed(2)}%</p>
                </div>
                <div className={getStatusColor(realtimeMetrics.api_availability >= 99.9)}>
                  {getStatusIcon(realtimeMetrics.api_availability >= 99.9)}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">P95 Latency</p>
                  <p className="text-2xl font-bold">{realtimeMetrics.api_latency_p95}ms</p>
                </div>
                <div className={getStatusColor(realtimeMetrics.api_latency_p95 < 500)}>
                  {getStatusIcon(realtimeMetrics.api_latency_p95 < 500)}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Error Rate</p>
                  <p className="text-2xl font-bold">{realtimeMetrics.error_rate.toFixed(2)}%</p>
                </div>
                <div className={getStatusColor(realtimeMetrics.error_rate < 1)}>
                  {getStatusIcon(realtimeMetrics.error_rate < 1)}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Content Success</p>
                  <p className="text-2xl font-bold">{realtimeMetrics.content_success_rate.toFixed(1)}%</p>
                </div>
                <div className={getStatusColor(realtimeMetrics.content_success_rate >= 98)}>
                  {getStatusIcon(realtimeMetrics.content_success_rate >= 98)}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs for different views */}
      <Tabs defaultValue="slos" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="slos">SLOs</TabsTrigger>
          <TabsTrigger value="error-budgets">Error Budgets</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="dependencies">Dependencies</TabsTrigger>
        </TabsList>

        {/* SLOs Tab */}
        <TabsContent value="slos" className="space-y-4">
          {slaStatus && Object.entries(slaStatus.slos).map(([key, slo]) => (
            <Card key={key}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">{slo.name}</CardTitle>
                  <Badge variant={slo.is_met ? "default" : "destructive"}>
                    {slo.is_met ? "Met" : "Not Met"}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{slo.description}</p>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-2">
                  <span>Compliance Rate</span>
                  <span className="font-semibold">{slo.compliance_rate.toFixed(2)}%</span>
                </div>
                <Progress value={slo.compliance_rate} className="mb-2" />
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Target: {slo.target}%</span>
                  <span>{slo.indicator_count} indicators</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Error Budgets Tab */}
        <TabsContent value="error-budgets" className="space-y-4">
          {slaStatus && Object.entries(slaStatus.error_budgets).map(([key, budget]) => (
            <Card key={key}>
              <CardHeader>
                <CardTitle className="text-lg">{key}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span>Remaining Budget</span>
                    <span className="font-semibold">{budget.remaining_minutes.toFixed(1)} minutes</span>
                  </div>
                  <Progress value={100 - budget.consumption_rate} className="mb-2" />
                  <div className="flex items-center justify-between text-sm">
                    <span>Consumption: {budget.consumption_rate.toFixed(1)}%</span>
                    <span className={getBurnRateColor(budget.burn_rate)}>
                      Burn Rate: {budget.burn_rate.toFixed(1)}x
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          {slaStatus && slaStatus.alerts.length > 0 ? (
            slaStatus.alerts.map((alert, index) => (
              <Alert key={index} className={getSeverityColor(alert.severity)}>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <div className="flex items-center justify-between">
                    <div>
                      <strong>{alert.slo}</strong> - {alert.message}
                    </div>
                    <Badge variant="outline">{alert.severity}</Badge>
                  </div>
                  <p className="text-xs mt-1">{new Date(alert.timestamp).toLocaleString()}</p>
                </AlertDescription>
              </Alert>
            ))
          ) : (
            <Card>
              <CardContent className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-2" />
                <p className="text-gray-600">No active alerts</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Dependencies Tab */}
        <TabsContent value="dependencies" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(dependencies).map(([name, dep]) => (
              <Card key={name}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base flex items-center gap-2">
                      {name === 'postgresql' && <Database className="w-4 h-4" />}
                      {name === 'redis' && <Server className="w-4 h-4" />}
                      {name.includes('api') && <Cloud className="w-4 h-4" />}
                      {name === 'cdn' && <Activity className="w-4 h-4" />}
                      {name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </CardTitle>
                    <Badge variant={dep.status === 'healthy' ? 'default' : 'destructive'}>
                      {dep.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-sm space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Latency</span>
                      <span>{dep.latency}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Last Check</span>
                      <span>{new Date(dep.last_check).toLocaleTimeString()}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SLADashboard;